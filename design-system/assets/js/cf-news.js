/**
 * Interactive News Archive: Client-side Topic Filtering & 2-column Pagination.
 */
(function() {
  'use strict';

  function initNewsArchive() {
    var grid = document.getElementById('cf-news-grid');
    if (!grid) return;

    var headerMetaSpan = document.querySelector('.cf-page-header__meta span');
    var countEl = document.querySelector('section[aria-labelledby="beitraege"] .cf-section-header__count');
    var isEn = document.documentElement.lang === 'en' || window.location.pathname.indexOf('/en/') !== -1;

    var allCards = Array.prototype.slice.call(grid.querySelectorAll('.cf-blog-card'));

    // Determine initial active topic
    var currentTopic = 'all';
    var activeTag = document.querySelector('.cf-article__tags .cf-article__tag[aria-current="page"]');
    if (activeTag && activeTag.getAttribute('data-filter-topic')) {
      currentTopic = activeTag.getAttribute('data-filter-topic');
    }

    function getWrap() {
      return document.getElementById('cf-news-more-wrap');
    }

    function getTopicLabel(topicSlug) {
      var tag = document.querySelector('.cf-article__tags .cf-article__tag[data-filter-topic="' + topicSlug + '"]');
      if (tag) return tag.textContent.trim();
      return topicSlug;
    }

    function updateHeaderMeta(matchingCount) {
      if (!headerMetaSpan) return;
      if (currentTopic === 'all') {
        headerMetaSpan.textContent = isEn
          ? matchingCount + ' posts since 2026'
          : matchingCount + ' Beiträge seit 2026';
      } else {
        var label = getTopicLabel(currentTopic);
        if (isEn) {
          var postWord = matchingCount === 1 ? 'post' : 'posts';
          headerMetaSpan.textContent = matchingCount + ' ' + postWord + ' on ' + label.toLowerCase();
        } else {
          var beitragWord = matchingCount === 1 ? 'Beitrag' : 'Beiträge';
          headerMetaSpan.textContent = matchingCount + ' ' + beitragWord + ' zum Thema ' + label;
        }
      }
    }

    function updateGrid() {
      var matching = allCards.filter(function(card) {
        if (currentTopic === 'all') return true;
        var topics = (card.getAttribute('data-topic') || '').toLowerCase().split(/\s+/);
        return topics.indexOf(currentTopic.toLowerCase()) !== -1;
      });

      // Hide non-matching cards completely
      allCards.forEach(function(card) {
        if (matching.indexOf(card) === -1) {
          card.classList.add('cf-blog-card--filtered-out');
        } else {
          card.classList.remove('cf-blog-card--filtered-out');
        }
      });

      // Show first 4 matching cards, hide the rest
      matching.forEach(function(card, index) {
        if (index < 4) {
          card.classList.remove('cf-blog-card--hidden');
        } else {
          card.classList.add('cf-blog-card--hidden');
        }
      });

      // Update post count
      if (countEl) {
        countEl.textContent = matching.length.toString();
      }

      // Update header meta text (e.g. "3 posts on grid operations")
      updateHeaderMeta(matching.length);

      // Update load more button visibility
      var wrap = getWrap();
      if (wrap) {
        var hiddenMatching = matching.filter(function(c) {
          return c.classList.contains('cf-blog-card--hidden');
        });
        wrap.classList.toggle('cf-news-more-wrap--empty', hiddenMatching.length === 0);
      }
    }

    // Global click listener with event delegation for Load More & Topic Chips
    document.addEventListener('click', function(e) {
      // 1. Handle Load More button click
      var moreBtn = e.target.closest('#cf-news-load-more');
      if (moreBtn) {
        e.preventDefault();
        var hiddenMatching = allCards.filter(function(card) {
          return !card.classList.contains('cf-blog-card--filtered-out') &&
                 card.classList.contains('cf-blog-card--hidden');
        });

        var batch = 4;
        for (var i = 0; i < Math.min(batch, hiddenMatching.length); i++) {
          hiddenMatching[i].classList.remove('cf-blog-card--hidden');
        }

        var remaining = allCards.filter(function(card) {
          return !card.classList.contains('cf-blog-card--filtered-out') &&
                 card.classList.contains('cf-blog-card--hidden');
        });

        var wrap = getWrap();
        if (wrap && remaining.length === 0) {
          wrap.classList.add('cf-news-more-wrap--empty');
        }
        return;
      }

      // 2. Handle Topic Filter click
      var link = e.target.closest('.cf-article__tag');
      if (!link) return;
      var parentTags = link.closest('.cf-article__tags');
      if (!parentTags) return;

      var topic = link.getAttribute('data-filter-topic');
      if (!topic) {
        var href = link.getAttribute('href') || '';
        if (href.indexOf('news.html') !== -1 || href === '' || href === '#') {
          topic = 'all';
        } else {
          var match = href.match(/([^\/\?#]+)\.html/);
          topic = match ? match[1].replace(/^news-thema-/, '') : 'all';
        }
      }

      e.preventDefault();
      e.stopPropagation();
      currentTopic = topic;

      // Update active chip state across all tags in .cf-article__tags
      var allTags = document.querySelectorAll('.cf-article__tags .cf-article__tag');
      allTags.forEach(function(tag) {
        var tagTopic = tag.getAttribute('data-filter-topic');
        if (!tagTopic) {
          var h = tag.getAttribute('href') || '';
          if (h.indexOf('news.html') !== -1 || h === '' || h === '#') tagTopic = 'all';
          else {
            var m = h.match(/([^\/\?#]+)\.html/);
            tagTopic = m ? m[1].replace(/^news-thema-/, '') : 'all';
          }
        }

        if (tagTopic === currentTopic) {
          tag.setAttribute('aria-current', 'page');
        } else {
          tag.removeAttribute('aria-current');
        }
      });

      updateGrid();
    });

    // Ensure grid displays correctly on initial load
    updateGrid();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initNewsArchive);
  } else {
    initNewsArchive();
  }
})();
