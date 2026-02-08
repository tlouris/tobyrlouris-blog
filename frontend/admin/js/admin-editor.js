/**
 * Post editor page logic — TinyMCE integration, create/edit post.
 */

let editId = null;

document.addEventListener('DOMContentLoaded', async () => {
    if (!(await checkAuth())) return;
    initSidebar();

    // Initialize TinyMCE
    tinymce.init({
        selector: '#content',
        height: 500,
        menubar: true,
        plugins: 'lists link image code table wordcount fullscreen',
        toolbar: 'undo redo | blocks | bold italic underline strikethrough | alignleft aligncenter alignright | bullist numlist | link image table | code fullscreen',
        content_style: "body { font-family: 'Open Sans', sans-serif; font-size: 16px; line-height: 1.7; }",
        branding: false,
        promotion: false
    });

    // Auto-generate slug from title
    document.getElementById('title').addEventListener('input', (e) => {
        if (!editId) {
            const slug = e.target.value
                .toLowerCase()
                .replace(/[^\w\s-]/g, '')
                .replace(/[\s_]+/g, '-')
                .replace(/-+/g, '-')
                .trim();
            document.getElementById('slug').value = slug;
        }
    });

    // Check if editing existing post
    const params = new URLSearchParams(window.location.search);
    editId = params.get('id');
    if (editId) {
        document.getElementById('pageTitle').textContent = 'Edit Post';
        loadPost(editId);
    }

    // Show image preview if URL is already populated (editing existing post)
    document.getElementById('image_url').addEventListener('input', updateImagePreview);

    // Form submission
    document.getElementById('postForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        await savePost();
    });
});

async function loadPost(id) {
    try {
        const post = await apiGet(`/posts/${id}`);
        if (!post) return;

        document.getElementById('title').value = post.title;
        document.getElementById('slug').value = post.slug;
        document.getElementById('category').value = post.category;
        document.getElementById('status').value = post.status;
        document.getElementById('reading_time').value = post.reading_time || '';
        document.getElementById('author').value = post.author;
        document.getElementById('image_url').value = post.image_url || '';
        updateImagePreview();
        document.getElementById('featured').checked = post.featured;
        document.getElementById('excerpt').value = post.excerpt;

        // Wait for TinyMCE to initialize, then set content
        const waitForEditor = setInterval(() => {
            const editor = tinymce.get('content');
            if (editor) {
                editor.setContent(post.content || '');
                clearInterval(waitForEditor);
            }
        }, 100);
    } catch (err) {
        showToast('Failed to load post: ' + err.message, 'error');
    }
}

async function savePost() {
    const btn = document.getElementById('saveBtn');
    btn.disabled = true;
    btn.textContent = 'Saving...';

    try {
        const editor = tinymce.get('content');
        const postData = {
            title: document.getElementById('title').value,
            slug: document.getElementById('slug').value || undefined,
            category: document.getElementById('category').value,
            status: document.getElementById('status').value,
            reading_time: document.getElementById('reading_time').value || undefined,
            author: document.getElementById('author').value,
            image_url: document.getElementById('image_url').value || undefined,
            featured: document.getElementById('featured').checked,
            excerpt: document.getElementById('excerpt').value,
            content: editor ? editor.getContent() : ''
        };

        if (editId) {
            await apiPut(`/posts/${editId}`, postData);
            showToast('Post updated successfully');
        } else {
            const result = await apiPost('/posts', postData);
            showToast('Post created successfully');
            if (result && result.id) {
                // Redirect to edit mode for the new post
                window.location.href = `post-editor.html?id=${result.id}`;
            }
        }
    } catch (err) {
        showToast('Failed to save: ' + err.message, 'error');
    } finally {
        btn.disabled = false;
        btn.textContent = 'Save Post';
    }
}

function updateImagePreview() {
    const url = document.getElementById('image_url').value;
    const preview = document.getElementById('imagePreview');
    const img = document.getElementById('imagePreviewImg');
    if (url) {
        img.src = url;
        preview.style.display = 'block';
    } else {
        preview.style.display = 'none';
    }
}

async function uploadImage(input) {
    const file = input.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    showToast('Uploading image...');

    try {
        const res = await fetch(`${ADMIN_API}/uploads/image`, {
            method: 'POST',
            credentials: 'include',
            body: formData,
        });

        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || 'Upload failed');
        }

        const data = await res.json();
        document.getElementById('image_url').value = data.url;
        updateImagePreview();
        showToast('Image uploaded successfully');
    } catch (err) {
        showToast('Upload failed: ' + err.message, 'error');
    }

    // Reset file input so the same file can be re-selected
    input.value = '';
}
