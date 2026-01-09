const express = require('express');
const path = require('path');

const app = express();

// Set COOP/COEP headers required by threaded WASM builds
app.use((req, res, next) => {
  res.setHeader('Cross-Origin-Opener-Policy', 'same-origin');
  res.setHeader('Cross-Origin-Embedder-Policy', 'require-corp');
  next();
});

app.use(express.static(path.join(__dirname, 'dist')));

const port = process.env.PORT || 8080;
app.listen(port, () => console.log(`Serving dist/ with COOP/COEP on http://localhost:${port}`));
