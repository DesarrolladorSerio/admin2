FROM postgres:15-alpine
RUN apk update && apk upgrade --no-cache && apk add --no-cache gosu
RUN ln -sf /usr/bin/gosu /usr/local/bin/gosu
