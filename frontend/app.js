// Тонкая обёртка над fetch: JSON туда-обратно и понятные ошибки FastAPI.
async function api(path, { method = "GET", body } = {}) {
    const options = {
        method,
        headers: { Accept: "application/json" },
    };

    if (body !== undefined) {
        options.headers["Content-Type"] = "application/json";
        options.body = JSON.stringify(body);
    }

    const response = await fetch(path, options);
    const text = await response.text();

    let data = null;
    if (text) {
        try {
            data = JSON.parse(text);
        } catch {
            data = text;
        }
    }

    if (!response.ok) {
        throw new Error(errorMessage(data, response.status));
    }

    return data;
}

function errorMessage(data, status) {
    if (data && Array.isArray(data.detail)) {
        return data.detail.map((item) => item.msg || String(item)).join("; ");
    }
    if (data && typeof data.detail === "string") {
        return data.detail;
    }
    if (typeof data === "string" && data) {
        return data;
    }
    return `Ошибка ${status}`;
}

function setMessage(element, text) {
    element.textContent = text;
}

// Регистрация
const registerForm = document.querySelector("#register-form");
const registerMessage = document.querySelector("#register-message");

registerForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const button = registerForm.querySelector("button");
    button.disabled = true;
    setMessage(registerMessage, "Отправка…");

    try {
        const data = await api("/register", {
            method: "POST",
            body: {
                email: registerForm.elements.email.value.trim(),
                password: registerForm.elements.password.value,
            },
        });
        setMessage(registerMessage, `${data.message} (${data.email})`);
        registerForm.reset();
    } catch (error) {
        setMessage(registerMessage, `Ошибка: ${error.message}`);
    } finally {
        button.disabled = false;
    }
});

// Создание поста
const postForm = document.querySelector("#post-form");
const postMessage = document.querySelector("#post-message");

postForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const button = postForm.querySelector("button");
    button.disabled = true;
    setMessage(postMessage, "Отправка…");

    try {
        const data = await api("/posts", {
            method: "POST",
            body: {
                title: postForm.elements.title.value.trim(),
                content: postForm.elements.content.value.trim(),
            },
        });
        postForm.reset();
        setMessage(postMessage, `Пост создан: #${data.id} «${data.title}»`);
        await loadPosts();
    } catch (error) {
        setMessage(postMessage, `Ошибка: ${error.message}`);
    } finally {
        button.disabled = false;
    }
});

// Список постов и действия с ними
const postsList = document.querySelector("#posts-list");
const postsMessage = document.querySelector("#posts-message");
const reloadButton = document.querySelector("#reload-posts");

function renderPost(post) {
    const item = document.createElement("li");
    item.dataset.id = String(post.id);

    const title = document.createElement("h3");
    title.textContent = `#${post.id} ${post.title}`;

    const content = document.createElement("p");
    content.className = "post-content";
    content.textContent = post.content;

    const actions = document.createElement("div");
    actions.className = "actions";

    const editButton = document.createElement("button");
    editButton.type = "button";
    editButton.textContent = "Редактировать";
    editButton.addEventListener("click", () => {
        startEdit(post, item);
    });

    const deleteButton = document.createElement("button");
    deleteButton.type = "button";
    deleteButton.textContent = "Удалить";
    deleteButton.addEventListener("click", () => {
        removePost(post, deleteButton);
    });

    actions.append(editButton, deleteButton);
    item.append(title, content, actions);
    return item;
}

function renderPosts(posts) {
    postsList.replaceChildren(...posts.map(renderPost));
}

function startEdit(post, item) {
    const form = document.createElement("form");
    form.className = "edit-form";
    form.innerHTML = `
        <label>Заголовок
            <input name="title" required maxlength="100">
        </label>
        <label>Текст
            <textarea name="content" rows="4" required maxlength="5000"></textarea>
        </label>
        <div class="actions">
            <button type="submit">Сохранить</button>
            <button type="button" class="cancel">Отмена</button>
        </div>
    `;

    form.elements.title.value = post.title;
    form.elements.content.value = post.content;

    form.querySelector(".cancel").addEventListener("click", () => {
        item.replaceWith(renderPost(post));
    });

    form.addEventListener("submit", async (event) => {
        event.preventDefault();

        const saveButton = form.querySelector('button[type="submit"]');
        saveButton.disabled = true;
        setMessage(postsMessage, "Сохранение…");

        try {
            await api(`/posts/${post.id}`, {
                method: "PATCH",
                body: {
                    title: form.elements.title.value.trim(),
                    content: form.elements.content.value.trim(),
                },
            });
            await loadPosts(`Пост #${post.id} сохранён.`);
        } catch (error) {
            saveButton.disabled = false;
            setMessage(postsMessage, `Ошибка: ${error.message}`);
        }
    });

    item.replaceChildren(form);
}

async function removePost(post, button) {
    if (!window.confirm(`Удалить пост #${post.id} «${post.title}»?`)) {
        return;
    }

    button.disabled = true;

    try {
        await api(`/posts/${post.id}`, { method: "DELETE" });
        await loadPosts(`Пост #${post.id} удалён.`);
    } catch (error) {
        button.disabled = false;
        setMessage(postsMessage, `Ошибка: ${error.message}`);
    }
}

async function loadPosts(message = "") {
    reloadButton.disabled = true;
    setMessage(postsMessage, "Загрузка…");

    try {
        const data = await api("/posts");

        if (!data || !Array.isArray(data.result)) {
            throw new Error("Неожиданный ответ сервера");
        }

        renderPosts(data.result);
        setMessage(
            postsMessage,
            message || (data.result.length ? "" : "Постов пока нет.")
        );
    } catch (error) {
        postsList.replaceChildren();
        setMessage(postsMessage, `Ошибка: ${error.message}`);
    } finally {
        reloadButton.disabled = false;
    }
}

reloadButton.addEventListener("click", () => loadPosts());
loadPosts();
