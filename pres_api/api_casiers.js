const http = require('http');
const url = require('url');

const PORT = 3000;

// État des casiers (ouvert/fermé)
const casiers = {};
for (let i = 1; i <= 15; i++) {
  casiers[i] = { status: 'fermé', lastOpened: null };
}

// File d'attente des casiers à ouvrir physiquement
let casierQueue = [];

const server = http.createServer((req, res) => {
  const parsedUrl = url.parse(req.url, true);
  const path = parsedUrl.pathname;
  const method = req.method;

  // Headers CORS
  res.setHeader('Content-Type', 'application/json');
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (method === 'OPTIONS') {
    res.writeHead(200);
    res.end();
    return;
  }

  // GET /casiers - Liste tous les casiers
  if (path === '/casiers' && method === 'GET') {
    res.writeHead(200);
    res.end(JSON.stringify(casiers, null, 2));
    return;
  }

  // POST /casier/:id/ouvrir - Ouvrir un casier spécifique (logique + queue physique)
  const ouvrirMatch = path.match(/^\/casier\/(\d+)\/ouvrir$/);
  if (ouvrirMatch && method === 'POST') {
    const casierId = parseInt(ouvrirMatch[1], 10);
    
    if (casierId >= 1 && casierId <= 15) {
      casiers[casierId].status = 'ouvert';
      casiers[casierId].lastOpened = new Date().toISOString();

      // Ajout dans la file d'attente pour ouverture physique par le Raspberry/Arduino
      casierQueue.push(casierId);
      
      res.writeHead(200);
      res.end(JSON.stringify({
        message: `Casier ${casierId} ajouté pour ouverture`,
        casier: casiers[casierId]
      }));
      return;
    } else {
      res.writeHead(404);
      res.end(JSON.stringify({ error: 'Casier non trouvé' }));
      return;
    }
  }

  // GET /casier/:id - Obtenir l'état d'un casier
  const casierMatch = path.match(/^\/casier\/(\d+)$/);
  if (casierMatch && method === 'GET') {
    const casierId = parseInt(casierMatch[1], 10);
    
    if (casierId >= 1 && casierId <= 15) {
      res.writeHead(200);
      res.end(JSON.stringify({
        id: casierId,
        ...casiers[casierId]
      }));
      return;
    } else {
      res.writeHead(404);
      res.end(JSON.stringify({ error: 'Casier non trouvé' }));
      return;
    }
  }

  // GET /next-casier - Prochain casier à ouvrir physiquement
  if (path === '/next-casier' && method === 'GET') {
    if (casierQueue.length > 0) {
      const nextCasier = casierQueue.shift(); // retire le premier de la queue
      res.writeHead(200);
      res.end(JSON.stringify({ casierId: nextCasier }));
    } else {
      res.writeHead(204); // No Content
      res.end();
    }
    return;
  }

  // Route non trouvée
  res.writeHead(404);
  res.end(JSON.stringify({ error: 'Route non trouvée' }));
});

server.listen(PORT, () => {
  console.log(`🚀 API des casiers démarrée sur http://localhost:${PORT}`);
  console.log('\nRoutes disponibles:');
  console.log('  GET  /casiers - Liste tous les casiers');
  console.log('  GET  /casier/:id - État d\'un casier (1-15)');
  console.log('  POST /casier/:id/ouvrir - Ouvrir un casier (1-15)');
  console.log('  GET  /next-casier - Prochain casier à ouvrir physiquement');
  console.log('\nExemples:');
  console.log('  curl http://localhost:3000/casiers');
  console.log('  curl http://localhost:3000/casier/1');
  console.log('  curl -X POST http://localhost:3000/casier/1/ouvrir');
  console.log('  curl http://localhost:3000/next-casier');
});