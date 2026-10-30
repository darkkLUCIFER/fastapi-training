import { afterEach, beforeEach, describe, it } from 'node:test';
import assert from 'node:assert/strict';

import { ApiError, auth, permissions, rolePermissions, todos, users } from '../src/api.js';


const storage = new Map();
let reloadCount = 0;

function jsonResponse(body, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json' },
  });
}


beforeEach(() => {
  storage.clear();
  reloadCount = 0;
  globalThis.localStorage = {
    getItem: (key) => storage.get(key) ?? null,
    setItem: (key, value) => storage.set(key, String(value)),
    removeItem: (key) => storage.delete(key),
  };
  globalThis.window = { location: { reload: () => { reloadCount += 1; } } };
});


afterEach(() => {
  delete globalThis.fetch;
  delete globalThis.localStorage;
  delete globalThis.window;
});


describe('API request handling', () => {
  it('sends JSON requests with the stored access token', async () => {
    storage.set('access_token', 'test-access-token');
    let request;
    globalThis.fetch = async (url, options) => {
      request = { url, options };
      return jsonResponse([{ id: 1 }]);
    };

    const result = await todos.list();

    assert.deepEqual(result, [{ id: 1 }]);
    assert.equal(request.url, '/todo/');
    assert.equal(request.options.headers.Authorization, 'Bearer test-access-token');
    assert.equal(request.options.headers['Content-Type'], 'application/json');
  });

  it('does not set JSON content type for URL-encoded bodies', async () => {
    let request;
    globalThis.fetch = async (url, options) => {
      request = options;
      return jsonResponse({ access_token: 'a', refresh_token: 'r' });
    };

    await auth.login('ada', 'password123');

    assert.equal(request.headers['Content-Type'], 'application/x-www-form-urlencoded');
    assert.ok(request.body instanceof URLSearchParams);
    assert.equal(request.body.get('username'), 'ada');
  });

  it('shares an in-flight GET request for the same endpoint and token', async () => {
    let calls = 0;
    let resolveFetch;
    globalThis.fetch = () => {
      calls += 1;
      return new Promise((resolve) => { resolveFetch = resolve; });
    };

    const first = users.me();
    const second = users.me();

    assert.equal(first, second);
    assert.equal(calls, 1);
    resolveFetch(jsonResponse({ id: 1 }));
    assert.deepEqual(await first, { id: 1 });
  });

  it('does not share GET requests that have caller-owned abort signals', async () => {
    let calls = 0;
    globalThis.fetch = async () => {
      calls += 1;
      return jsonResponse({ id: calls });
    };

    const first = permissions.list({ signal: new AbortController().signal });
    const second = permissions.list({ signal: new AbortController().signal });

    assert.deepEqual(await Promise.all([first, second]), [{ id: 1 }, { id: 2 }]);
    assert.equal(calls, 2);
  });

  it('converts a 204 response to null', async () => {
    globalThis.fetch = async () => new Response(null, { status: 204 });

    assert.equal(await todos.delete(4, { id: 1, role: 'user' }), null);
  });

  it('clears credentials and reloads after an unauthorized response', async () => {
    storage.set('access_token', 'expired-access');
    storage.set('refresh_token', 'expired-refresh');
    globalThis.fetch = async () => jsonResponse({ detail: 'expired' }, 401);

    await assert.rejects(users.me(), (error) => {
      assert.ok(error instanceof ApiError);
      assert.equal(error.status, 401);
      return true;
    });

    assert.equal(storage.has('access_token'), false);
    assert.equal(storage.has('refresh_token'), false);
    assert.equal(reloadCount, 1);
  });

  it('formats FastAPI validation errors', async () => {
    globalThis.fetch = async () => jsonResponse(
      { detail: [{ msg: 'title is required' }, { msg: 'priority is invalid' }] },
      422,
    );

    await assert.rejects(todos.list(), (error) => {
      assert.equal(error.message, 'title is required, priority is invalid');
      assert.equal(error.status, 422);
      return true;
    });
  });

  it('falls back to a bounded plain-text server error', async () => {
    globalThis.fetch = async () => new Response('x'.repeat(250), { status: 502 });

    await assert.rejects(permissions.list(), (error) => {
      assert.equal(error.status, 502);
      assert.equal(error.message.length, 200);
      return true;
    });
  });

  it('uses the login response error detail when login fails', async () => {
    globalThis.fetch = async () => jsonResponse({ detail: 'Invalid credentials' }, 400);

    await assert.rejects(auth.login('ada', 'wrong'), { message: 'Invalid credentials' });
  });

  it('sends role-permission create, update and delete to their expected routes', async () => {
    const requests = [];
    globalThis.fetch = async (url, options) => {
      requests.push({ url, options });
      return options.method === 'DELETE' ? new Response(null, { status: 204 }) : jsonResponse({ ok: true });
    };

    await rolePermissions.create({ role: 'admin', permission_id: 2 });
    await rolePermissions.update(7, { role: 'admin', permission_id: 2, access: false });
    await rolePermissions.remove(7);

    assert.deepEqual(requests.map(({ url, options }) => [url, options.method]), [
      ['/admin/role-permission/create/', 'POST'],
      ['/admin/role-permission/7/', 'PATCH'],
      ['/admin/role-permission/7/', 'DELETE'],
    ]);
  });
});
