import logging

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .base import BaseApiWrapperMixin
from .exceptions import D365ApiError, D365ApiWrapperError

logger = logging.getLogger(__name__)

class SyncBaseApiWrapper(BaseApiWrapperMixin):
    DEFAULT_TIMEOUT = 20

    def __init__(self, *args, timeout=None, retries=3, backoff_factor=0.5, **kwargs):
        super().__init__(*args, **kwargs)
        self.timeout = timeout or self.DEFAULT_TIMEOUT
        self._session = requests.Session()

        retry_strategy = Retry(
            total=retries,
            backoff_factor=backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST", "PUT", "PATCH", "DELETE"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self._session.mount("http://", adapter)
        self._session.mount("https://", adapter)

    def _request(self, method, url, **kwargs):
        kwargs.setdefault("timeout", self.timeout)
        try:
            return self._session.request(method, url, **kwargs)
        except requests.exceptions.RequestException as e:
            logger.warning(f"D365 API request failed after retries: {e}")
            raise D365ApiError({'request': str(e)})

    def get_page(self, page=1, select=None, request_filter=None, order_by=None, annotations=None, query_dict=None):
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
        response = self._request('GET', self.api_url, params=params, headers=headers)
        if response.ok:
            self.current_page = page
            return response.json()
        raise D365ApiError({'status': response.status_code, 'data': response.text})

    def get_next_page(self):
        if not self.current_page:
            raise D365ApiWrapperError('Call get_page() first to set current page.')
        return self.get_page(page=self.current_page + 1)

    def get_previous_page(self):
        if not self.current_page or self.current_page == 1:
            raise D365ApiWrapperError('No previous page. Already at the first page.')
        return self.get_page(page=self.current_page - 1)

    def get_top(self, qty, select=None, request_filter=None, order_by=None, annotations=None, query_dict=None):
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
        response = self._request('GET', self.api_url, params=params, headers=headers)
        if response.status_code == 200:
            return response.json()
        raise D365ApiError({'status': response.status_code, 'data': response.text})

    def create(self, data, annotations=None):
        headers = self.headers.copy()
        headers.update({'Prefer': 'return=representation'})
        if annotations:
            headers = self._update_prefer_header(headers, 'odata.include-annotations', f'"{annotations}"')
        return self._request('POST', self.api_url, headers=headers, json=data)

    def retrieve(self, entity_id, select=None, annotations=None, query_dict=None):
        params = {}
        if select:
            params['$select'] = select
        if query_dict:
            params.update(query_dict)
        headers = self.headers.copy()
        if annotations:
            headers = self._update_prefer_header(headers, 'odata.include-annotations', f'"{annotations}"')
        return self._request('GET', f'{self.api_url}({entity_id})', params=params, headers=headers)

    def update(self, entity_id, data, select=None, annotations=None):
        headers = self.headers.copy()
        headers = self._update_prefer_header(headers, 'return', 'representation')
        if annotations:
            headers = self._update_prefer_header(headers, 'odata.include-annotations', f'"{annotations}"')
        url = f'{self.api_url}({entity_id})'
        params = {}
        if select:
            params['$select'] = select
        return self._request('PATCH', url, params=params, headers=headers, json=data)

    def delete(self, entity_id):
        return self._request('DELETE', f'{self.api_url}({entity_id})', headers=self.headers)