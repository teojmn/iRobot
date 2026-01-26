document.addEventListener('DOMContentLoaded', function() {
    loadCasiers();
    loadEmprunts();
});

async function loadCasiers() {
    try {
        const response = await fetch('/api/casiers');
        const casiers = await response.json();
        
        // Update stats
        document.getElementById('total-casiers').textContent = casiers.length;
        
        const disponibles = casiers.filter(c => c.statut === 'disponible').length;
        const occupes = casiers.filter(c => c.statut === 'occupe').length;
        const maintenance = casiers.filter(c => c.statut === 'maintenance').length;
        
        document.getElementById('casiers-disponibles').textContent = disponibles;
        document.getElementById('casiers-occupes').textContent = occupes;
        document.getElementById('casiers-maintenance').textContent = maintenance;
        
        // Update table
        const tbody = document.querySelector('#casiers-table tbody');
        tbody.innerHTML = '';
        
        casiers.forEach(casier => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${casier.id}</td>
                <td>${casier.numero}</td>
                <td>${casier.etage}</td>
                <td><span class="status ${casier.statut}">${casier.statut}</span></td>
                <td>${casier.derniere_maj || 'N/A'}</td>
            `;
            tbody.appendChild(tr);
        });
    } catch (error) {
        console.error('Erreur lors du chargement des casiers:', error);
    }
}

async function loadEmprunts() {
    try {
        const response = await fetch('/api/emprunts');
        const emprunts = await response.json();
        
        const tbody = document.querySelector('#emprunts-table tbody');
        tbody.innerHTML = '';
        
        emprunts.slice(0, 10).forEach(emprunt => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${emprunt.id}</td>
                <td>${emprunt.casier_id}</td>
                <td>${emprunt.utilisateur}</td>
                <td>${emprunt.date_debut}</td>
                <td>${emprunt.date_fin || 'En cours'}</td>
            `;
            tbody.appendChild(tr);
        });
    } catch (error) {
        console.error('Erreur lors du chargement des emprunts:', error);
    }
}