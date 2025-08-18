from flask_caching import Cache
from flask_compress import Compress

cache = Cache()

compress = Compress()
compress.cache = cache
compress.cache_key = lambda request: request.url
