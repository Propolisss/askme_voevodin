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


for (const question of questionCards) {
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

for (const answer of answerCards) {
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
