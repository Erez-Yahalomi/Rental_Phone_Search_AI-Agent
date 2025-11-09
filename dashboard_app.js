async function fetchSummaries(searchId) {
    const res = await fetch(`/dashboard/summaries?search_id=${encodeURIComponent(searchId)}`);
    const data = await res.json();
    return data.items || [];
  }
  
  function render(items) {
    const app = document.getElementById('app');
    const grid = document.createElement('div');
    grid.className = 'grid';
    items.forEach(item => {
      const card = document.createElement('div');
      card.className = 'card';
      const title = document.createElement('h2');
      title.textContent = item.listing_details.address || item.listing_details.title || 'Rental';
      const meta = document.createElement('div');
      meta.className = 'meta';
      const price = item.listing_details.price ? `$${item.listing_details.price}` : '';
      meta.textContent = `${price} • ${item.listing_details.beds || '?'} bd / ${item.listing_details.baths || '?'} ba`;
      const link = document.createElement('a');
      link.href = item.listing_details.url || '#';
      link.target = '_blank';
      link.textContent = 'View listing';
      const summary = document.createElement('div');
      summary.className = 'summary';
      summary.textContent = item.summary_text || 'No summary yet.';
      card.appendChild(title);
      card.appendChild(meta);
      card.appendChild(link);
      card.appendChild(summary);
      grid.appendChild(card);
    });
    app.innerHTML = '';
    app.appendChild(grid);
  }
  
  (async function init() {
    const searchId = new URL(location.href).searchParams.get('searchId') || 'latest';
    const items = await fetchSummaries(searchId);
    render(items);
  })();
  