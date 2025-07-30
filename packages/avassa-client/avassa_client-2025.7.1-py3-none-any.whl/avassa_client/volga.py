# SPDX-License-Identifier: Apache-2.0

import enum
import json
import logging
import os
import ssl
import websockets
import websockets.legacy
import websockets.legacy.client

from typing import Optional, Union
from avassa_client import Session

logger = logging.getLogger(__name__)
new_websockets = websockets.connect != websockets.legacy.client.Connect

logging.getLogger('websockets').setLevel(os.environ.get('WEBSOCKETS_LOGLEVEL', 'WARNING'))


class Topic(object):
    def __init__(self, enum, topic, child_site=None):
        self._enum = enum
        self._topic = topic
        self._child_site = child_site

    @classmethod
    def local(cls, topic: str) -> 'Topic':
        return cls('local', topic)

    @classmethod
    def parent(cls, topic: str) -> 'Topic':
        return cls('parent', topic)

    @classmethod
    def child_site(cls, topic: str, child_site: str) -> 'Topic':
        return cls('child-site', topic, child_site)

    def get_fields(self):
        d = {'location': self._enum,
             'topic': self._topic}
        if self._child_site is not None:
            d['child-site'] = self._child_site
        return d


class Position(object):
    def __init__(self, enum, key=None, value=None):
        self._enum = enum
        self._key = key
        self._value = value

    @classmethod
    def beginning(cls) -> 'Position':
        return cls('beginning')

    @classmethod
    def end(cls) -> 'Position':
        return cls('end')

    @classmethod
    def unread(cls) -> 'Position':
        return cls('unread')

    @classmethod
    def since(cls, duration: str) -> 'Position':
        return cls('since', 'position-since', duration)

    @classmethod
    def seqno(cls, sequence_number: int) -> 'Position':
        return cls('seqno', 'position-sequence-number', sequence_number)

    @classmethod
    def timestamp(cls, timestamp: int) -> 'Position':
        return cls('timestamp', 'position-timestamp', timestamp)

    def get_fields(self):
        if self._key is not None:
            return {self._key: self._value}
        return {'position': self._enum}


class Encryption(enum.Enum):
    SIGNATURE = 'signature'
    FULL = 'full'


class CreateOptions(object):
    def __init__(self, enum, opts=None):
        self._enum = enum
        self._opts = opts

    @classmethod
    def wait(cls) -> 'CreateOptions':
        return cls('wait')

    @classmethod
    def fail(cls) -> 'CreateOptions':
        return cls('fail')

    @classmethod
    def create(cls,
               fmt: str,
               replication_factor: Optional[int] = None,
               persistence: Optional[str] = None,
               local_placement: Optional[bool] = None,
               num_chunks: Optional[int] = None,
               max_size: Optional[str] = None,
               max_days: Optional[int] = None,
               encryption: Optional[Encryption] = None,
               transit_key: Optional[str] = None,
               ephemeral: Optional[bool] = None) -> 'CreateOptions':
        create_opts = {'format': fmt}
        if replication_factor is not None:
            create_opts['replication-factor'] = replication_factor
        if persistence is not None:
            create_opts['persistence'] = persistence
        if local_placement is not None:
            create_opts['local-placement'] = local_placement
        if num_chunks is not None:
            create_opts['num-chunks'] = num_chunks
        if max_size is not None:
            create_opts['max-size'] = max_size
        if max_days is not None:
            create_opts['max_days'] = max_days
        if encryption is not None:
            create_opts['encryption'] = encryption.value
        if transit_key is not None:
            create_opts['transit-key'] = transit_key
        if ephemeral is not None:
            create_opts['ephemeral'] = ephemeral
        return cls('create', create_opts)

    def get_fields(self):
        d = {'on-no-exists': self._enum}
        if self._enum == 'create':
            d['create-options'] = self._opts
        return d


class ResponseDecodeError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message


class ResponseError(Exception):
    def __init__(self, message: str, errors: list) -> None:
        self.message = message
        self.errors = errors


def decode_result(res):
    try:
        msg = json.loads(res.decode('utf-8'))
        result = msg['result']
    except Exception as e:
        raise ResponseDecodeError("Unable to decode response") from e
    if result == 'error':
        errors = msg.get('errors', [])
        if len(errors) > 1:
            raise ResponseError("Multiple errors", errors)
        elif len(errors) == 1:
            raise ResponseError(errors[0].get('error-message', 'Unknown error'), errors)
        else:
            raise ResponseError("Unknown error", errors)
    elif result != 'ok':
        raise ResponseError(f'Strange result: {result}', None)
    return msg

class VolgaClient(object):
    async def _close(self):
        la = self._ws.local_address
        await self._ws.close()
        self.log.debug('Closed socket %s', la)

    async def __aenter__(self):
        ssl_context = self._session.get_ssl_context()
        hostname = self._session.get_server_hostname()
        pname = 'additional_headers' if new_websockets else 'extra_headers'
        kwargs = {'ssl': ssl_context,
                  pname: self._session.auth_header(),
                  'server_hostname': hostname}
        self._ws = await websockets.connect(self._session.get_volga_ws_url(), **kwargs)
        try:
            self.log.debug('Opened socket %s', self._ws.local_address)
            await self._open()
            return self
        except Exception:
            await self._close()
            raise

    async def __aexit__(self, *args, **kwargs):
        await self._close()


class Producer(VolgaClient):
    def __init__(self,
                 session: Session,
                 producer_name: str,
                 topic: Topic,
                 on_no_exists: CreateOptions) -> None:
        self._session = session
        self._producer_name = producer_name
        self._topic = topic
        self._on_no_exists = on_no_exists
        self.log = logger.getChild(__class__.__name__)

    async def _open(self) -> None:
        cmd = {
            "op": "open-producer",
            "name": self._producer_name,
        }
        cmd.update(self._topic.get_fields())
        cmd.update(self._on_no_exists.get_fields())

        self.log.debug("_open payload: %s", cmd)
        await self._ws.send(json.dumps(cmd, ensure_ascii=False).encode('utf-8'))

        res = await self._ws.recv()
        self.log.debug("_open res: %s", res)
        decode_result(res)

    async def produce(self, payload: Union[str, dict]) -> None:
        cmd = {
            "op": "produce",
            "sync": "sync",
            "payload": payload
        }
        self.log.debug("produce payload: %s", cmd)
        await self._ws.send(json.dumps(cmd).encode('utf-8'))
        res = await self._ws.recv()
        self.log.debug("produce res: %s", res)
        return decode_result(res)

    async def recv(self):
        return await self._ws.recv()

    async def ping(self, data):
        return await self._ws.ping(data)


class InfraProducer(VolgaClient):
    def __init__(self,
                 session: Session,
                 producer_name: str,
                 infra: str) -> None:
        self._session = session
        self._producer_name = producer_name
        self._infra = infra
        self.log = logger.getChild(__class__.__name__)

    async def _open(self) -> None:
        cmd = {
            "op": "open-infra-producer",
            "infra": self._infra
        }

        self.log.debug("_open_infra_producer payload: %s", cmd)
        await self._ws.send(json.dumps(cmd).encode('utf-8'))

        res = await self._ws.recv()
        self.log.debug("_open_infra_producer res: %s", res)
        decode_result(res)

    async def produce(self,
                      direction: str,
                      payload: Union[str, dict],
                      local_site_deliver: Optional[str]=None,
                      destination_sites: Optional[list]=None) -> None:
        cmd = {
            "op": "infra-produce",
            "direction": direction,
            "payload": payload
        }
        if local_site_deliver:
            cmd['local-site-deliver'] = local_site_deliver
        if destination_sites:
            dst = [{'site': x} for x in destination_sites]
            cmd['destination-sites'] = dst

        self.log.debug("produce payload: %s", cmd)
        await self._ws.send(json.dumps(cmd).encode('utf-8'))
        res = await self._ws.recv()
        self.log.debug("produce res: %s", res)
        return decode_result(res)

    async def recv(self):
        return await self._ws.recv()

    async def ping(self, data):
        return await self._ws.ping(data)


class Consumer(VolgaClient):
    def __init__(self,
                 session: Session,
                 consumer_name: str,
                 mode: str,
                 position: Position,
                 topic: Topic,
                 on_no_exists: CreateOptions,
                 end_marker: Optional[bool] = None,
                 re_match: Optional[str] = None,
                 invert_match: Optional[bool] = None) -> None:
        self._session = session
        self._topic = topic
        self._consumer_name = consumer_name
        self._mode = mode
        self._position = position
        self._on_no_exists = on_no_exists
        self._end_marker = end_marker
        self._re_match = re_match
        self._invert_match = invert_match
        self.log = logger.getChild(__class__.__name__)
        self.last_seqno = 0

    async def _open(self) -> None:
        cmd = {
            "op": "open-consumer",
            "name": self._consumer_name,
            "mode": self._mode,
        }
        cmd.update(self._topic.get_fields())
        cmd.update(self._position.get_fields())
        cmd.update(self._on_no_exists.get_fields())
        if self._end_marker is not None:
            cmd['end-marker'] = self._end_marker
        if self._re_match is not None:
            cmd['re-match'] = self._re_match
        if self._invert_match:
            cmd['invert-match'] = True
        self.log.debug("_open_consumer payload: %s", cmd)
        await self._ws.send(json.dumps(cmd).encode('utf-8'))

        res = await self._ws.recv()
        self.log.debug("_open_consumer res: %s", res)
        decode_result(res)

    async def more(self, n):
        cmd = {
            "op": "more",
            "n": n
        }
        self.log.debug("more payload: %s", cmd)
        await self._ws.send(json.dumps(cmd).encode('utf-8'))

    async def recv(self, auto_more=10):
        msg_raw = await self._ws.recv()
        msg = json.loads(msg_raw.decode('utf-8'))
        self.log.debug("recv %s", msg_raw)
        if auto_more and (msg['remain'] == 0):
            await self.more(auto_more)
        seqno = msg.get('seqno')
        if seqno is not None:
            self.last_seqno = seqno
        return msg

    async def ack(self, seqno=None):
        """Acknowledge a message. If no seqno is provided, acknowledge the most
        recently received message."""
        if seqno is None:
            seqno = self.last_seqno
        cmd = {
            "op": "ack",
            "seqno": seqno
        }
        self.log.debug("ack payload: %s", cmd)
        await self._ws.send(json.dumps(cmd, ensure_ascii=False).encode('utf-8'))


class InfraConsumer(Consumer):
    def __init__(self,
                 session: Session,
                 consumer_name: str,
                 mode: str,
                 position: Position,
                 infra: str,
                 end_marker: Optional[bool] = None,
                 re_match: Optional[str] = None,
                 invert_match: Optional[bool] = None) -> None:
        self._session = session
        self._infra = infra
        self._consumer_name = consumer_name
        self._mode = mode
        self._position = position
        self._end_marker = end_marker
        self._re_match = re_match
        self._invert_match = invert_match
        self.log = logger.getChild(__class__.__name__)
        self.last_seqno = 0

    async def __aexit__(self, *args, **kwargs):
        await self._close()

    async def _open(self) -> None:
        cmd = {
            "op": "open-infra-consumer",
            "name": self._consumer_name,
            "mode": self._mode,
            "infra": self._infra
        }
        cmd.update(self._position.get_fields())
        if self._end_marker is not None:
            cmd['end-marker'] = self._end_marker
        if self._re_match is not None:
            cmd['re-match'] = self._re_match
        if self._invert_match:
            cmd['invert-match'] = True

        self.log.debug("_open_infra_consumer payload: %s", cmd)
        await self._ws.send(json.dumps(cmd).encode('utf-8'))

        res = await self._ws.recv()
        self.log.debug("_open_infra_consumer res: %s", res)
        decode_result(res)

    async def more(self, n):
        cmd = {
            "op": "more",
            "n": n
        }
        self.log.debug("more payload: %s", cmd)
        await self._ws.send(json.dumps(cmd).encode('utf-8'))

    async def recv(self, auto_more=10):
        msg_raw = await self._ws.recv()
        msg = json.loads(msg_raw.decode('utf-8'))
        self.log.debug("recv %s", msg_raw)
        if auto_more and (msg['remain'] == 0):
            await self.more(auto_more)
        seqno = msg.get('seqno')
        if seqno is not None:
            self.last_seqno = seqno
        return msg

    async def ack(self, seqno=None):
        """Acknowledge a message. If no seqno is provided, acknowledge the most
        recently received message."""
        if seqno is None:
            seqno = self.last_seqno
        cmd = {
            "op": "ack",
            "seqno": seqno
        }
        self.log.debug("ack payload: %s", cmd)
        await self._ws.send(json.dumps(cmd, ensure_ascii=False).encode('utf-8'))


class QueryConsumer(VolgaClient):
    """Deprecated. Use QueryTopicsConsumer instead"""
    def __init__(self,
                 session: Session,
                 query: dict):
        self._query = query
        self._session = session
        self.log = logger.getChild(__class__.__name__)

    async def _open(self) -> None:
        cmd = {
            "op": "query-topics"
        }
        cmd.update(self._query)

        self.log.debug("_open_query_consumer payload: %s", cmd)
        await self._ws.send(json.dumps(cmd).encode('utf-8'))

    async def recv(self):
        try:
            data = await self._ws.recv()
            self.log.debug("data %s", data)
            return data
        except websockets.exceptions.ConnectionClosedOK:
            return None


class QueryTopicsConsumer(VolgaClient):
    def __init__(self,
                 session: Session,
                 query: dict):
        self.validate_query(query)
        self._query = query
        self._session = session
        self.log = logger.getChild(__class__.__name__)

    def validate_query(self, query):
        for topic in query.get('topics', []):
            output = topic.get('output', {})
            if output.get('payload-only', False) == True:
                raise ValueError('payload-only is not supported by this client')

    async def _open(self) -> None:
        cmd = {
            "op": "query-topics",
            "auto-more": False
        }
        self._query.update(cmd)

        self.log.debug("_open_query_topics_consumer payload: %s", self._query)
        await self._ws.send(json.dumps(self._query).encode('utf-8'))

        res = await self._ws.recv()
        self.log.debug("_open_query_topics_consumer res: %s", res)
        decode_result(res)


    async def more(self, n):
        cmd = {
            "op": "more",
            "n": n
        }
        self.log.debug("more payload: %s", cmd)
        await self._ws.send(json.dumps(cmd).encode('utf-8'))

    async def recv(self, auto_more=10):
        try:
            msg_raw = await self._ws.recv()
            self.log.debug("recv %s", msg_raw)
            msg = json.loads(msg_raw.decode('utf-8'))
            if auto_more and (msg['remain'] == 0):
                await self.more(auto_more)

            return msg
        except websockets.exceptions.ConnectionClosedOK:
            return None


async def change_options(session: Session,
                         topic: Topic,
                         num_chunks: Optional[int] = None,
                         max_size: Optional[str] = None,
                         max_days: Optional[int] = None):
    ssl_context = session.get_ssl_context()
    hostname = session.get_server_hostname()
    pname = 'additional_headers' if new_websockets else 'extra_headers'
    kwargs = {'ssl': ssl_context,
              pname: session.auth_header(),
              'server_hostname': hostname}
    async with websockets.connect(session.get_volga_ws_url(), **kwargs) as ws:
        cmd = {'op': 'change-options'}
        cmd.update(topic.get_fields())
        if num_chunks is not None:
            cmd.update({'num-chunks': num_chunks})
        if max_size is not None:
            cmd.update({'max-size': max_size})
        if max_days is not None:
            cmd.update({'max-days': max_days})

        logger.debug('change_options payload: %s', cmd)
        await ws.send(json.dumps(cmd).encode('utf-8'))
        res = await ws.recv()
        logger.debug('change_options res: %s', res)
        return res.decode('utf-8')


async def delete_topic(session: Session, topic: Union[str, Topic]):
    if isinstance(topic, str):
        logger.warning('Calling delete_topic with topic as string is deprecated. Use Topic object instead.')
        topic = Topic.local(topic)
    ssl_context = session.get_ssl_context()
    hostname = session.get_server_hostname()
    pname = 'additional_headers' if new_websockets else 'extra_headers'
    kwargs = {'ssl': ssl_context,
              pname: session.auth_header(),
              'server_hostname': hostname}
    async with websockets.connect(session.get_volga_ws_url(), **kwargs) as ws:
        cmd = {'op': 'delete-topic'}
        cmd.update(topic.get_fields())

        logger.debug('delete_topic payload: %s', cmd)
        await ws.send(json.dumps(cmd).encode('utf-8'))
        res = await ws.recv()
        logger.debug('delete_topic res: %s', res)
        return res.decode('utf-8')
