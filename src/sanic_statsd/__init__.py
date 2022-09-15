import time

from sanic import Sanic


class SanicStatsD:
    def __init__(self, app=None, statsd=None, tags=None, metric='api.response.time'):
        self.statsd = statsd
        self.tags = tags
        self.metric = metric
        # If an app was provided, then call `init_app` for them
        if app is not None:
            self.init_app(app)
        else:
            self.app = None

    def init_app(self, app: Sanic):
        """hook on request start etc."""
        app.register_middleware(self.statsd_start_timers, 'request')
        app.register_middleware(self.statsd_submit_timers, 'response')

    async def statsd_start_timers(self, request):
        request.ctx.started_at = time.time()

    async def statsd_submit_timers(self, request, response):
        elapsed = time.time() - request.ctx.started_at
        tags = [
            'method:{}'.format(request.method.lower()),
            'uri_template:{}'.format(request.uri_template)
        ]
        if self.tags:
            tags.extend(self.tags)
        # TODO - implement support for https://github.com/jsocol/pystatsd
        # (impediment: what to to with tags?)
        self.statsd.histogram(self.metric, elapsed, tags=tags)
