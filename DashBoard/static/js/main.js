document.addEventListener('DOMContentLoaded', function() {
    loadCasiers();
    loadEmprunts();
    
    // Rafraîchir toutes les 10 secondes
    setInterval(() => {
        loadCasiers();
        loadEmprunts();
    }, 10000);
});

async function loadCasiers() {
    try {
        const response = await fetch('/data/casiers');
        const casiers = await response.json();
        
        // Update stats
        document.getElementById('total-casiers').textContent = casiers.length;
        
        const disponibles = casiers.filter(c => c.statut === 'disponible').length;
        const occupes = casiers.filter(c => c.statut === 'occupe').length;
        
        document.getElementById('casiers-disponibles').textContent = disponibles;
        document.getElementById('casiers-occupes').textContent = occupes;
        
        // Update table
        const tbody = document.querySelector('#casiers-table tbody');
        tbody.innerHTML = '';
        
        if (casiers.length === 0) {
            tbody.innerHTML = '<tr><td colspan="3" style="text-align: center; color: var(--muted);">Aucun casier disponible</td></tr>';
            return;
        }
        
        casiers.forEach(casier => {
            const tr = document.createElement('tr');
            const badgeClass = casier.statut === 'disponible' ? 'disponible' : 'occupe';
            const statusText = casier.statut === 'disponible' ? 'Disponible' : 'Occupé';
            
            tr.innerHTML = `
                <td>${casier.numero}</td>
                <td>${casier.etat}</td>
                <td><span class="badge ${badgeClass}">${statusText}</span></td>
            `;
            tbody.appendChild(tr);
        });
    } catch (error) {
        console.error('Erreur lors du chargement des casiers:', error);
        document.querySelector('#casiers-table tbody').innerHTML = 
            '<tr><td colspan="3" style="text-align: center; color: var(--danger);">Erreur de chargement</td></tr>';
    }
}

async function loadEmprunts() {
    try {
        const response = await fetch('/data/emprunts');
        const emprunts = await response.json();
        
        const tbody = document.querySelector('#emprunts-table tbody');
        tbody.innerHTML = '';
        
        if (emprunts.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" style="text-align: center; color: var(--muted);">Aucun emprunt enregistré</td></tr>';
            return;
        }
        
        // Afficher les 10 derniers emprunts
        emprunts.slice(-10).reverse().forEach(emprunt => {
            const tr = document.createElement('tr');
            const statutClass = emprunt.statut === 'EN COURS' ? 'en-cours' : '';
            
            tr.innerHTML = `
                <td>${emprunt.id}</td>
                <td>${emprunt.casier_id}</td>
                <td>${emprunt.utilisateur}</td>
                <td>${emprunt.date_debut}</td>
                <td><span class="badge ${statutClass}">${emprunt.statut}</span></td>
            `;
            tbody.appendChild(tr);
        });
    } catch (error) {
        console.error('Erreur lors du chargement des emprunts:', error);
        document.querySelector('#emprunts-table tbody').innerHTML = 
            '<tr><td colspan="5" style="text-align: center; color: var(--danger);">Erreur de chargement</td></tr>';
    }
}