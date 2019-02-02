


# 1. build docker

    $docker build --no-cache -t disxss docker

# 2. docker

    $docker run -v $(pwd):/app/disxss -p 9000:8080  -it disxss:latest /bin/bash


# 3. Once inside  docker, start mongodb and flask server

    $ cd disxss && docker/startup.sh &



# 4. In local machine, outside docker, in browser fetch url

    http://127.0.0.1:9000/
