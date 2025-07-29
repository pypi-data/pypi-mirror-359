# d365_wrapper/async_.py

import asyncio
import logging

import aiohttp

from .base import BaseApiWrapperMixin
from .exceptions import D365ApiError, D365ApiWrapperError

logger = logging.getLogger(__name__)

class AsyncBaseApiWrapper(BaseApiWrapperMixin):
    DEFAULT_TIMEOUT = 20

    def __init__(self, *args, timeout=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.timeout = timeout or self.DEFAULT_TIMEOUT
        self._session = None

    async def _get_session(self):
        if self._session is None:
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            self._session = aiohttp.ClientSession(timeout=timeout)
        return self._session

    async def close(self):
        if self._session:
            await self._session.close()
            self._session = None

    async def get_page(self, page=1, select=None, request_filter=None, order_by=None, annotations=None, query_dict=None):
        headers = self.headers.copy()
        headers.update({'Prefer': f'odata.maxpagesize={self.page_size}'})
        if annotations:
            headers = self._update_prefer_header(headers, 'odata.include-annotations', f'"{annotations}"')
        params = {'$count': 'true'}
        if self._api_url.startswith('/api/data/v'):
            params['$skiptoken'] = f'<cookie pagenumber="{page}" istracking="False" />'
        elif page > 1:
            params['$top'] = self.page_size
            params['$skip'] = self.page_size * (page - 1)
        if select:
            params['$select'] = select
        if request_filter:
            params['$filter'] = request_filter
        if order_by:
            params['$orderby'] = order_by
        if query_dict:
            params.update(query_dict)

        session = await self._get_session()
        try:
            async with session.get(self.api_url, params=params, headers=headers) as response:
                self.current_page = page
                if response.status == 200:
                    return await response.json()
                raise D365ApiError({'status': response.status, 'data': await response.text()})
        except asyncio.TimeoutError:
            raise D365ApiError({'status': 504, 'data': 'Request timed out'})
        except Exception as e:
            raise D365ApiError({'status': 502, 'data': str(e)})

    async def get_next_page(self):
        if not self.current_page:
            raise D365ApiWrapperError('Call get_page() first to set current page.')
        return await self.get_page(page=self.current_page + 1)

    async def get_previous_page(self):
        if not self.current_page or self.current_page == 1:
            raise D365ApiWrapperError('No previous page. Already at the first page.')
        return await self.get_page(page=self.current_page - 1)

    async def get_top(self, qty, select=None, request_filter=None, order_by=None, annotations=None, query_dict=None):
        params = {'$top': qty}
        if select:
            params['$select'] = select
        if request_filter:
            params['$filter'] = request_filter
        if order_by:
            params['$orderby'] = order_by
        if query_dict:
            params.update(query_dict)
        headers = self.headers.copy()
        if annotations:
            headers = self._update_prefer_header(headers, 'odata.include-annotations', f'"{annotations}"')

        session = await self._get_session()
        async with session.get(self.api_url, params=params, headers=headers) as response:
            if response.status == 200:
                return await response.json()
            raise D365ApiError({'status': response.status, 'data': await response.text()})

    async def create(self, data, annotations=None):
        headers = self.headers.copy()
        headers.update({'Prefer': 'return=representation'})
        if annotations:
            headers = self._update_prefer_header(headers, 'odata.include-annotations', f'"{annotations}"')
        session = await self._get_session()
        async with session.post(self.api_url, headers=headers, json=data) as response:
            return await response.json()

    async def retrieve(self, entity_id, select=None, annotations=None, query_dict=None):
        params = {}
        if select:
            params['$select'] = select
        if query_dict:
            params.update(query_dict)
        headers = self.headers.copy()
        if annotations:
            headers = self._update_prefer_header(headers, 'odata.include-annotations', f'"{annotations}"')
        url = f'{self.api_url}({entity_id})'
        session = await self._get_session()
        async with session.get(url, params=params, headers=headers) as response:
            return await response.json()

    async def update(self, entity_id, data, select=None, annotations=None):
        headers = self.headers.copy()
        headers = self._update_prefer_header(headers, 'return', 'representation')
        if annotations:
            headers = self._update_prefer_header(headers, 'odata.include-annotations', f'"{annotations}"')
        params = {}
        if select:
            params['$select'] = select
        url = f'{self.api_url}({entity_id})'
        session = await self._get_session()
        async with session.patch(url, params=params, headers=headers, json=data) as response:
            return await response.json()

    async def delete(self, entity_id):
        url = f'{self.api_url}({entity_id})'
        session = await self._get_session()
        async with session.delete(url, headers=self.headers) as response:
            return response.status
