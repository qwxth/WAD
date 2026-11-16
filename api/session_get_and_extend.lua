local user_id = redis.call('GET', KEYS[1])
if user_id then
    redis.call('EXPIRE', KEYS[1], ARGV[1])
end
return user_id
