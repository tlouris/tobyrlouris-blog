// ============================================
// Technology Innovations for Water Industry
// Main JavaScript File
// ============================================

// Configuration
const CONFIG = {
  API_BASE_URL: window.location.hostname === 'localhost'
    ? 'http://localhost:8000/api'
    : `${window.location.protocol}//${window.location.hostname}/api`,
  POSTS_PER_PAGE: 9,
  SEARCH_DEBOUNCE_MS: 300
};

// ============================================
// STATE MANAGEMENT
// ============================================
const state = {
  posts: [],
  filteredPosts: [],
  currentCategory: 'all',
  currentPage: 1,
  searchQuery: '',
  isLoading: false
};

// ============================================
// DOM READY
// ============================================
document.addEventListener('DOMContentLoaded', () => {
  initializeApp();
});

// ============================================
// INITIALIZATION
// ============================================
function initializeApp() {
  // Initialize mobile menu
  initMobileMenu();

  // Initialize search
  initSearch();

  // Initialize filters
  initFilters();

  // Initialize forms
  initForms();

  // Log visitor
  logVisitor();

  // Set active nav
  setActiveNav();

  // Initialize page-specific features
  const page = document.body.dataset.page;
  switch(page) {
    case 'home':
      loadFeaturedPost();
      loadRecentPosts(6);
      break;
    case 'blogs':
      loadAllPosts();
      break;
    case 'category':
      loadCategoryPosts();
      break;
    case 'post':
      loadComments();
      break;
  }
}

// ============================================
// MOBILE MENU
// ============================================
function initMobileMenu() {
  const toggle = document.querySelector('.mobile-menu-toggle');
  const nav = document.querySelector('.main-nav');

  if (toggle && nav) {
    toggle.addEventListener('click', () => {
      nav.classList.toggle('active');
      const isOpen = nav.classList.contains('active');
      toggle.setAttribute('aria-expanded', isOpen);
      toggle.innerHTML = isOpen ? '✕' : '☰';
    });
  }
}

// ============================================
// NAVIGATION
// ============================================
function setActiveNav() {
  const currentPath = window.location.pathname;
  const navLinks = document.querySelectorAll('.main-nav a');

  navLinks.forEach(link => {
    if (link.getAttribute('href') === currentPath ||
        (currentPath.includes(link.getAttribute('href')) && link.getAttribute('href') !== '/')) {
      link.classList.add('active');
    }
  });
}

// ============================================
// VISITOR LOGGING
// ============================================
async function logVisitor() {
  try {
    const visitorData = {
      page: window.location.pathname,
      referrer: document.referrer,
      user_agent: navigator.userAgent,
      timestamp: new Date().toISOString()
    };

    await fetch(`${CONFIG.API_BASE_URL}/visitor-log`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(visitorData)
    });
  } catch (error) {
    console.error('Error logging visitor:', error);
  }
}

// ============================================
// SEARCH FUNCTIONALITY
// ============================================
function initSearch() {
  const searchInput = document.querySelector('.search-input');
  if (!searchInput) return;

  let debounceTimer;
  searchInput.addEventListener('input', (e) => {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => {
      state.searchQuery = e.target.value.toLowerCase();
      filterPosts();
    }, CONFIG.SEARCH_DEBOUNCE_MS);
  });
}

// ============================================
// FILTER FUNCTIONALITY
// ============================================
function initFilters() {
  const filterTags = document.querySelectorAll('.filter-tag');

  filterTags.forEach(tag => {
    tag.addEventListener('click', () => {
      // Remove active class from all tags
      filterTags.forEach(t => t.classList.remove('active'));

      // Add active class to clicked tag
      tag.classList.add('active');

      // Update state
      state.currentCategory = tag.dataset.category;
      state.currentPage = 1;

      // Filter posts
      filterPosts();
    });
  });
}

function filterPosts() {
  if (state.posts.length === 0) return;

  state.filteredPosts = state.posts.filter(post => {
    // Category filter
    const categoryMatch = state.currentCategory === 'all' ||
                         post.category === state.currentCategory;

    // Search filter
    const searchMatch = state.searchQuery === '' ||
                       post.title.toLowerCase().includes(state.searchQuery) ||
                       post.excerpt.toLowerCase().includes(state.searchQuery) ||
                       post.category.toLowerCase().includes(state.searchQuery);

    return categoryMatch && searchMatch;
  });

  renderPosts();
}

// ============================================
// BLOG POSTS LOADING
// ============================================
async function loadFeaturedPost() {
  const container = document.querySelector('.featured-post');
  if (!container) return;

  try {
    const response = await fetch(`${CONFIG.API_BASE_URL}/posts/featured`);
    const post = await response.json();

    container.innerHTML = `
      <div class="featured-post-image" style="background-image: url(${post.image || '/images/default-post.jpg'})"></div>
      <div class="featured-post-content">
        <span class="featured-badge">Featured Article</span>
        <div class="post-meta">
          <span class="post-category">${post.category}</span>
          <span>${post.date}</span>
          <span>${post.reading_time}</span>
        </div>
        <h2><a href="/post.html?id=${post.id}">${post.title}</a></h2>
        <p class="post-excerpt">${post.excerpt}</p>
        <a href="/post.html?id=${post.id}" class="read-more">Read Full Article →</a>
      </div>
    `;
  } catch (error) {
    console.error('Error loading featured post:', error);
    container.innerHTML = '<p class="loading">Featured post coming soon...</p>';
  }
}

async function loadRecentPosts(limit = 6) {
  const container = document.querySelector('.posts-grid');
  if (!container) return;

  container.innerHTML = '<p class="loading">Loading posts...</p>';

  try {
    const response = await fetch(`${CONFIG.API_BASE_URL}/posts?limit=${limit}`);
    const posts = await response.json();
    state.posts = posts;

    renderPostsGrid(posts, container);
  } catch (error) {
    console.error('Error loading posts:', error);
    renderPlaceholderPosts(container);
  }
}

async function loadAllPosts() {
  const container = document.querySelector('.posts-grid');
  if (!container) return;

  container.innerHTML = '<p class="loading">Loading posts...</p>';

  try {
    const response = await fetch(`${CONFIG.API_BASE_URL}/posts`);
    const posts = await response.json();
    state.posts = posts;
    state.filteredPosts = posts;

    renderPosts();
  } catch (error) {
    console.error('Error loading all posts:', error);
    renderPlaceholderPosts(container);
  }
}

async function loadCategoryPosts() {
  const urlParams = new URLSearchParams(window.location.search);
  const category = urlParams.get('category');
  if (!category) return;

  const container = document.querySelector('.posts-grid');
  if (!container) return;

  container.innerHTML = '<p class="loading">Loading posts...</p>';

  try {
    const response = await fetch(`${CONFIG.API_BASE_URL}/posts?category=${category}`);
    const posts = await response.json();
    state.posts = posts;

    renderPostsGrid(posts, container);
  } catch (error) {
    console.error('Error loading category posts:', error);
    renderPlaceholderPosts(container);
  }
}

function renderPosts() {
  const container = document.querySelector('.posts-grid');
  if (!container) return;

  renderPostsGrid(state.filteredPosts, container);
}

function renderPostsGrid(posts, container) {
  if (posts.length === 0) {
    container.innerHTML = '<p class="loading">No posts found.</p>';
    return;
  }

  container.innerHTML = posts.map(post => `
    <article class="post-card fade-in">
      <div class="post-card-image" style="background-image: url(${post.image || '/images/default-post.jpg'})"></div>
      <div class="post-card-content">
        <div class="post-meta">
          <span class="post-category">${post.category}</span>
          <span>${post.date}</span>
          <span>${post.reading_time || '5 min read'}</span>
        </div>
        <h3><a href="/post.html?id=${post.id}">${post.title}</a></h3>
        <p class="post-excerpt">${post.excerpt}</p>
        <a href="/post.html?id=${post.id}" class="read-more">Read More →</a>
      </div>
    </article>
  `).join('');
}

// Placeholder posts for when API is not available
function renderPlaceholderPosts(container) {
  const placeholderPosts = [
    {
      id: 1,
      category: 'Digital Strategy',
      date: '2025-01-15',
      title: 'Digital Transformation in Wastewater Treatment: A Roadmap',
      excerpt: 'Exploring how digital technologies are revolutionizing wastewater treatment operations and creating new opportunities for efficiency.',
      image: null
    },
    {
      id: 2,
      category: 'Cybersecurity & Resilience',
      date: '2025-01-12',
      title: 'Protecting Critical Water Infrastructure from Cyber Threats',
      excerpt: 'Best practices for securing SCADA systems and operational technology in wastewater facilities against emerging cyber risks.',
      image: null
    },
    {
      id: 3,
      category: 'Project Lessons',
      date: '2025-01-08',
      title: 'Lessons from a Major SCADA System Upgrade',
      excerpt: 'Key insights and practical lessons learned from implementing a modern SCADA system at a regional wastewater treatment plant.',
      image: null
    },
    {
      id: 4,
      category: 'Industry Trends & Regulation',
      date: '2025-01-05',
      title: 'EPA Cybersecurity Requirements: What You Need to Know',
      excerpt: 'Understanding new federal regulations for cybersecurity in water and wastewater utilities and how to achieve compliance.',
      image: null
    },
    {
      id: 5,
      category: 'Digital Strategy',
      date: '2024-12-20',
      title: 'IoT Sensors: The Future of Water Quality Monitoring',
      excerpt: 'How Internet of Things technology is enabling real-time monitoring and predictive maintenance in wastewater systems.',
      image: null
    },
    {
      id: 6,
      category: 'Cybersecurity & Resilience',
      date: '2024-12-15',
      title: 'Building Cyber Resilience in Small Water Systems',
      excerpt: 'Practical, budget-conscious approaches to cybersecurity for smaller wastewater treatment facilities and utilities.',
      image: null
    }
  ];

  renderPostsGrid(placeholderPosts, container);
}

// ============================================
// COMMENTS SYSTEM
// ============================================
async function loadComments() {
  const commentsContainer = document.querySelector('.comments-list');
  if (!commentsContainer) return;

  const urlParams = new URLSearchParams(window.location.search);
  const postId = urlParams.get('id');
  if (!postId) return;

  try {
    const response = await fetch(`${CONFIG.API_BASE_URL}/comments?post_id=${postId}`);
    const comments = await response.json();

    if (comments.length === 0) {
      commentsContainer.innerHTML = '<p>No comments yet. Be the first to comment!</p>';
      return;
    }

    commentsContainer.innerHTML = comments.map(comment => `
      <div class="comment">
        <div class="comment-author">${escapeHtml(comment.author)}</div>
        <div class="comment-date">${formatDate(comment.date)}</div>
        <div class="comment-content">${escapeHtml(comment.content)}</div>
      </div>
    `).join('');
  } catch (error) {
    console.error('Error loading comments:', error);
    commentsContainer.innerHTML = '<p>Comments coming soon...</p>';
  }
}

// ============================================
// FORM HANDLING
// ============================================
function initForms() {
  // Contact form
  const contactForm = document.querySelector('#contact-form');
  if (contactForm) {
    contactForm.addEventListener('submit', handleContactSubmit);
  }

  // Comment form
  const commentForm = document.querySelector('#comment-form');
  if (commentForm) {
    commentForm.addEventListener('submit', handleCommentSubmit);
  }

  // Newsletter form
  const newsletterForm = document.querySelector('#newsletter-form');
  if (newsletterForm) {
    newsletterForm.addEventListener('submit', handleNewsletterSubmit);
  }
}

async function handleContactSubmit(e) {
  e.preventDefault();

  const form = e.target;
  const submitBtn = form.querySelector('button[type="submit"]');
  const originalText = submitBtn.textContent;

  submitBtn.disabled = true;
  submitBtn.textContent = 'Sending...';

  const formData = {
    name: form.querySelector('#name').value,
    email: form.querySelector('#email').value,
    organization: form.querySelector('#organization').value,
    topic: form.querySelector('#topic').value,
    message: form.querySelector('#message').value
  };

  try {
    const response = await fetch(`${CONFIG.API_BASE_URL}/contact`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(formData)
    });

    if (response.ok) {
      showMessage('Thank you! Your message has been sent successfully.', 'success');
      form.reset();
    } else {
      throw new Error('Failed to send message');
    }
  } catch (error) {
    console.error('Error submitting contact form:', error);
    showMessage('Sorry, there was an error sending your message. Please try again.', 'error');
  } finally {
    submitBtn.disabled = false;
    submitBtn.textContent = originalText;
  }
}

async function handleCommentSubmit(e) {
  e.preventDefault();

  const form = e.target;
  const submitBtn = form.querySelector('button[type="submit"]');
  const originalText = submitBtn.textContent;

  submitBtn.disabled = true;
  submitBtn.textContent = 'Submitting...';

  const urlParams = new URLSearchParams(window.location.search);
  const postId = urlParams.get('id');

  const commentData = {
    post_id: postId,
    author: form.querySelector('#comment-name').value,
    email: form.querySelector('#comment-email').value,
    content: form.querySelector('#comment-content').value
  };

  try {
    const response = await fetch(`${CONFIG.API_BASE_URL}/comments`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(commentData)
    });

    if (response.ok) {
      showMessage('Thank you! Your comment is pending moderation and will appear soon.', 'success');
      form.reset();
    } else {
      throw new Error('Failed to submit comment');
    }
  } catch (error) {
    console.error('Error submitting comment:', error);
    showMessage('Sorry, there was an error submitting your comment. Please try again.', 'error');
  } finally {
    submitBtn.disabled = false;
    submitBtn.textContent = originalText;
  }
}

async function handleNewsletterSubmit(e) {
  e.preventDefault();

  const form = e.target;
  const submitBtn = form.querySelector('button[type="submit"]');
  const originalText = submitBtn.textContent;

  submitBtn.disabled = true;
  submitBtn.textContent = 'Subscribing...';

  const email = form.querySelector('input[type="email"]').value;

  try {
    const response = await fetch(`${CONFIG.API_BASE_URL}/newsletter`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email })
    });

    if (response.ok) {
      showMessage('Thank you for subscribing!', 'success');
      form.reset();
    } else {
      throw new Error('Failed to subscribe');
    }
  } catch (error) {
    console.error('Error subscribing to newsletter:', error);
    showMessage('Sorry, there was an error. Please try again.', 'error');
  } finally {
    submitBtn.disabled = false;
    submitBtn.textContent = originalText;
  }
}

// ============================================
// UTILITY FUNCTIONS
// ============================================
function showMessage(message, type = 'info') {
  // Create message element
  const messageEl = document.createElement('div');
  messageEl.className = `message message-${type}`;
  messageEl.textContent = message;
  messageEl.style.cssText = `
    position: fixed;
    top: 100px;
    left: 50%;
    transform: translateX(-50%);
    background-color: ${type === 'success' ? '#28a745' : type === 'error' ? '#dc3545' : '#17a2b8'};
    color: white;
    padding: 1rem 2rem;
    border-radius: 4px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    z-index: 10000;
    animation: slideDown 0.3s ease-out;
  `;

  document.body.appendChild(messageEl);

  // Remove after 5 seconds
  setTimeout(() => {
    messageEl.style.animation = 'slideUp 0.3s ease-out';
    setTimeout(() => messageEl.remove(), 300);
  }, 5000);
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

function formatDate(dateString) {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });
}

// Add CSS for message animations
const style = document.createElement('style');
style.textContent = `
  @keyframes slideDown {
    from {
      opacity: 0;
      transform: translateX(-50%) translateY(-20px);
    }
    to {
      opacity: 1;
      transform: translateX(-50%) translateY(0);
    }
  }

  @keyframes slideUp {
    from {
      opacity: 1;
      transform: translateX(-50%) translateY(0);
    }
    to {
      opacity: 0;
      transform: translateX(-50%) translateY(-20px);
    }
  }
`;
document.head.appendChild(style);

// ============================================
// SERVICE WORKER REGISTRATION
// ============================================
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js')
      .then(registration => console.log('SW registered'))
      .catch(err => console.log('SW registration failed'));
  });
}
