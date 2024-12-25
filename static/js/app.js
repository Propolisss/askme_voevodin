const questionCards = document.getElementsByClassName('question-card');
const answerCards = document.getElementsByClassName('answer-card');

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


function registerAnswer(answer) {
    const answerLikeButton = answer.querySelector('.answer-like-button');
    const answerDislikeButton = answer.querySelector('.answer-dislike-button');
    const answerId = answer.id;
    const like_count = answer.querySelector('.like-count');
    const checkBox = answer.querySelector('.form-check');

    answerLikeButton.addEventListener('click', () => {
        const request = new Request(`/answer-like/${answerId}`, {
            method: "POST",
            body: JSON.stringify({is_liked: true}),
            headers: {'X-CSRFToken': getCookie('csrftoken')},
            mode: 'same-origin'
        });

        fetch(request).then(response => {
            response.json().then((data) => {
                like_count.innerHTML = data.answer_likes_count;
            })
        });
        answerLikeButton.disabled = true;
        answerDislikeButton.disabled = false;
    });


    answerDislikeButton.addEventListener('click', () => {
        const request = new Request(`/answer-like/${answerId}`, {
            method: "POST",
            body: JSON.stringify({is_liked: false}),
            headers: {'X-CSRFToken': getCookie('csrftoken')},
            mode: 'same-origin'
        });

        fetch(request).then(response => {
            response.json().then((data) => {
                like_count.innerHTML = data.answer_likes_count;
            })
        });
        answerLikeButton.disabled = false;
        answerDislikeButton.disabled = true;
    });

    checkBox.addEventListener('change', () => {
        const checked = checkBox.querySelector('.form-check-input').checked;
        const request = new Request(`/answer/${answerId}`, {
            method: "POST",
            body: JSON.stringify({correct: checked}),
            headers: {'X-CSRFToken': getCookie('csrftoken')},
            mode: 'same-origin'
        });

        fetch(request).then(response => {
            response.json().then(data => {
                if (!data.success) {
                    alert('error');
                }
            })
        })
    });
}

function registerQuestion(question) {
    const questionLikeButton = question.querySelector('.question-like-button');
    const questionDislikeButton = question.querySelector('.question-dislike-button');
    const questionId = question.id;
    const like_count = question.querySelector('.like-count');


    questionLikeButton.addEventListener('click', () => {
        const request = new Request(`/question-like/${questionId}`, {
            method: "POST",
            body: JSON.stringify({is_liked: true}),
            headers: {'X-CSRFToken': getCookie('csrftoken')},
            mode: 'same-origin'
        })

        fetch(request).then(response => {
            response.json().then((data) => {
                like_count.innerHTML = data.question_likes_count;
            })
        });
        questionLikeButton.disabled = true;
        questionDislikeButton.disabled = false;
    });

    questionDislikeButton.addEventListener('click', () => {
        const request = new Request(`/question-like/${questionId}`, {
            method: "POST",
            body: JSON.stringify({is_liked: false}),
            headers: {'X-CSRFToken': getCookie('csrftoken')},
            mode: 'same-origin'
        })

        fetch(request).then(response => {
            response.json().then((data) => {
                like_count.innerHTML = data.question_likes_count;
            })
        });
        questionLikeButton.disabled = false;
        questionDislikeButton.disabled = true;
    });
}

for (const question of questionCards) {
    registerQuestion(question);
}

for (const answer of answerCards) {
    registerAnswer(answer);
}


const searchInput = document.querySelector('.search');
const searchSuggestions = document.querySelector('.search-suggestions');

function debounce(func, delay) {
    let timeout;
    return function (...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), delay);
    };
}

async function searchQuestions(text) {
    if (!text) {
        return;
    }

    searchSuggestions.innerHTML = '<div class="suggestion-item searching">Ищем...</div>';
    searchSuggestions.style.display = 'block';

    try {
        const response = await fetch(`/search/${encodeURIComponent(text)}`, {
            headers: {'X-CSRFToken': getCookie('csrftoken')},
        });
        console.log('response: ', response);

        const data = await response.json();
        console.log('data: ', data);

        const suggestions = JSON.parse(data.suggestions);

        displaySuggestions(suggestions);
    } catch (error) {
        console.error('Error fetching search results:', error);
    }
}

function displaySuggestions(suggestions) {
    searchSuggestions.innerHTML = '';

    if (suggestions.length === 0) {
        const noResultsElement = document.createElement('div');
        noResultsElement.className = 'suggestion-item no-results';
        noResultsElement.textContent = 'Нет результатов';
        searchSuggestions.appendChild(noResultsElement);
    } else {
        suggestions.forEach(suggestion => {
            console.log(suggestion);
            const question = suggestion.fields;
            const suggestionElement = document.createElement('div');
            suggestionElement.className = 'suggestion-item';
            suggestionElement.innerHTML = `
                    <h3>${question.title}</h3>
                    <p>${question.text}</p>
                `;

            suggestionElement.addEventListener('click', () => {
                window.location.href = `/question/${suggestion.pk}`;
            });

            searchSuggestions.appendChild(suggestionElement);
        });
    }

    searchSuggestions.style.display = 'block';
}

const debouncedSearch = debounce(searchQuestions, 500);
searchInput.addEventListener('input', (event) => {
    debouncedSearch(event.target.value);
});

document.addEventListener('click', (event) => {
    const isClickInside = event.target.closest('.search-suggestions') || event.target.closest('.search');
    if (!isClickInside) {
        searchSuggestions.style.display = 'none';
    }
});

window.addEventListener('scroll', () => {
    searchSuggestions.style.display = 'none';
});
