FROM node:22-slim

ENV NODE_ENV=production

WORKDIR /app

RUN groupadd --system app && useradd --system --gid app --home-dir /app app

EXPOSE 3000

USER app

CMD ["node", "-e", "console.log('TritonPath frontend placeholder: Next.js app code is not implemented yet. Container is ready.'); setInterval(() => {}, 1 << 30);"]
