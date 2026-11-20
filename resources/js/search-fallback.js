/* Metadata-only search fallback for Gaddel. Does not change or restore OpenSearch. */
let syriacaFallbackIndexPromise = null;

function loadSyriacaFallbackIndex() {
    if (!syriacaFallbackIndexPromise) {
        syriacaFallbackIndexPromise = fetch('/search-index.json')
            .then(response => {
                if (!response.ok) throw new Error(`Index HTTP ${response.status}`);
                return response.json();
            })
            .then(data => {
                if (!Array.isArray(data) || !data.length || !data.every(x => x && typeof x.idno === 'string')) {
                    throw new Error('Fallback index missing or invalid');
                }
                return data;
            })
            .catch(error => {
                syriacaFallbackIndexPromise = null; // retry on next search
                throw error;
            });
    }
    return syriacaFallbackIndexPromise;
}

function syriacaPlain(value) {
    return (Array.isArray(value) ? value.join(' ') : String(value ?? '')).toLocaleLowerCase().trim();
}

function syriacaFallbackNotice(message) {
    const container = document.getElementById('search-info');
    if (!container) return;
    const notice = document.createElement('p');
    notice.className = 'fallback-notice';
    notice.textContent = message;
    container.appendChild(notice);
}

async function fallbackSearch() {
    const params = buildQueryParams();
    const supported = new Set(['from', 'size', 'q', 'keyword', 'title', 'author', 'persName', 'placeName', 'idno', 'series', 'sort', 'lang']);
    const ignored = new Set(['letter']); // initialized by the page even for non-letter searches
    const unsupported = Object.entries(params)
        .filter(([key, val]) => !supported.has(key) && !ignored.has(key) && val !== '' && val !== undefined)
        .map(([key]) => key);

    // Browsing, CBSS author/subject special searches and advanced filters rely on OpenSearch.
    if (unsupported.length) {
        displayResultsInfo(0);
        handleError('search-results', 'OpenSearch is unavailable. Local backup supports basic metadata search only; these filters require OpenSearch: ' + unsupported.join(', '));
        syriacaFallbackNotice('Local search backup could not run this advanced query.');
        return;
    }

    try {
        const index = await loadSyriacaFallbackIndex();
        const queryFields = ['q', 'keyword', 'title', 'author', 'persName', 'placeName', 'idno'];
        const active = queryFields.filter(key => syriacaPlain(params[key]));
        const recordFields = ['displayTitleEnglish', 'title', 'author', 'persName', 'placeName', 'idno'];
        const seriesQuery = syriacaPlain(params.series);
        const matches = index.filter(record => {
            if (seriesQuery && !syriacaPlain(record.series).includes(seriesQuery)) return false;
            return active.every(field => {
                const term = syriacaPlain(params[field]);
                const targets = field === 'q' || field === 'keyword' ? recordFields : [field];
                return targets.some(key => syriacaPlain(record[key]).includes(term));
            });
        });

        const from = Math.max(0, Number(params.from) || 0);
        const size = Math.max(1, Number(params.size) || 25);
        const data = {
            hits: {
                total: { value: matches.length },
                hits: matches.slice(from, from + size).map(record => ({ _source: record }))
            }
        };
        state.totalResults = matches.length;
        clearSearchResults();
        displayResultsInfo(matches.length);
        // Generic result renderer avoids requiring fields missing from CBSS-specific records.
        displayResults(data);
        // Remove stale pagination from an earlier successful OpenSearch response.
        document.querySelectorAll('.searchPagination').forEach(el => { el.innerHTML = ''; });
        if (matches.length > size) {
            renderPagination(matches.length, size, state.currentPage, changePage);
        }
        syriacaFallbackNotice('OpenSearch is unavailable. Showing local metadata-only results (not fuzzy/full-text search). This index may be older than the live data.');
    } catch (error) {
        console.error('[search] JSON fallback unavailable:', error);
        handleError('search-results', 'Search is temporarily unavailable: OpenSearch and the local JSON backup could not be reached.');
    }
}
