const localtunnel = require('localtunnel');

(async () => {
  console.log("=== Starting Localtunnel ===");
  try {
    const tunnel = await localtunnel({ port: 8000 });
    console.log(`Tunnel URL: ${tunnel.url}`);
    
    tunnel.on('close', () => {
      console.log("Tunnel closed.");
    });
  } catch (err) {
    console.error(`Error: ${err.message}`);
    process.exit(1);
  }
})();
