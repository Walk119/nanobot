import request from '@/utils/request';

export function fileTree() {
return request({
    url: '/users',
    method: 'get',
  });
}