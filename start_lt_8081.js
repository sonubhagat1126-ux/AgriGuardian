const localtunnel = require('localtunnel');

(async () => {
  console.log("=== Starting Localtunnel on 8081 ===");
  try {
    const tunnel = await localtunnel({ port: 8081 });
    console.log(`Tunnel URL: ${tunnel.url}`);
    
    tunnel.on('close', () => {
      console.log("Tunnel closed.");
    });
  } catch (err) {
    console.error(`Error: ${err.message}`);
    process.exit(1);
  }
})();
