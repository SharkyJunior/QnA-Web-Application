function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');

const questionContainers = document.querySelectorAll('.card__likes[data-content-id]');

const answerContainers = document.querySelectorAll('.question__answer[data-content-id]');

function initializeUserVotes() {
    console.log('Initializing user votes...');
    
    const voteContainers = document.querySelectorAll('.card__likes[data-content-id]');
    
    voteContainers.forEach(container => {
        const userVote = container.dataset.userVote;
        if (userVote) {
            updateButtonStyles(container, userVote);
        }
    });
    
    console.log(`Initialized ${voteContainers.length} vote containers`);
}

function handleVote(e) {
    const button = e.currentTarget;
    const container = button.closest('.card__likes');
    
    if (!container) {
        console.error('Container not found');
        return;
    }
    
    const objectId = container.dataset.contentId;
    const objectType = container.dataset.contentType;
    const voteType = button.dataset.voteType; 
    
    if (!objectId || !objectType || !voteType) {
        console.error('Missing data attributes');
        return;
    }
    
    const counter = container.querySelector('.vote-counter');
    if (!counter) {
        console.error('Counter not found in container');
        return;
    }

    const currentCount = parseInt(counter.textContent) || 0;
    
    fetch('/api/vote/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({
            object_type: objectType,
            object_id: objectId,
            vote_type: voteType
        })
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(errorData => {
                throw new Error(errorData.error);
            }).catch(() => {
                if (response.status === 401) {
                    throw new Error('Вы не авторизованы');
                }
                throw new Error(`HTTP error ${response.status}`);
            });
        }
        return response.json();
    })
    .then(data => {
        console.log('Success response:', data);
        
        counter.textContent = data.new_rating;
            
        console.log('Before updateButtonStyles:', {
            container: container,
            user_vote: data.user_vote
        });
        
        updateButtonStyles(container, data.user_vote);
        
        console.log('Vote successful!');
    })
    .catch(error => {
        counter.textContent = currentCount;
        console.error('Full error details:', error);
        console.error('Error name:', error.name);
        console.error('Error message:', error.message);
        console.error('Error stack:', error.stack);
        
        alert('Произошла ошибка: ' + error.message);
    })
}

function updateButtonStyles(container, userVote) {
    if (!container) {
        console.error('updateButtonStyles: container is null');
        return;
    }
    
    const upvoteBtn = container.querySelector('[data-vote-type="upvote"]');
    const downvoteBtn = container.querySelector('[data-vote-type="downvote"]');

    if (!upvoteBtn || !downvoteBtn) {
        console.error('updateButtonStyles: buttons not found', {
            container: container,
            upvoteBtn: upvoteBtn,
            downvoteBtn: downvoteBtn
        });
        return;
    }
    
    console.log('updateButtonStyles:', {
        userVote: userVote,
        upvoteBtn: upvoteBtn,
        downvoteBtn: downvoteBtn
    });
    
    upvoteBtn.classList.remove('btn-secondary');
    upvoteBtn.classList.remove('btn-success');
    downvoteBtn.classList.remove('btn-secondary');
    downvoteBtn.classList.remove('btn-danger');
    
    if (userVote === 'upvote') {
        upvoteBtn.classList.add('btn-success')
        downvoteBtn.classList.add('btn-secondary');
    } else if (userVote === 'downvote') {
        downvoteBtn.classList.add('btn-danger')
        upvoteBtn.classList.add('btn-secondary');
    } else {
        downvoteBtn.classList.add('btn-secondary');
        upvoteBtn.classList.add('btn-secondary');
    }
}

function updateTick(container, correct) {
    const tick = container.querySelector('.correct-tick');
    if (tick) {
        tick.checked = Boolean(correct);
    }

    console.log('updateTick:', {
        container: container,
        correct: correct
    });
}

function initializeVoteSystem() {
    console.log('Initializing vote system...');
    
    initializeUserVotes();
    
    const voteButtons = document.querySelectorAll('.vote-btn');
    voteButtons.forEach(button => {
        button.removeEventListener('click', handleVote);
        button.addEventListener('click', handleVote);
    });
    
    console.log(`Initialized ${voteButtons.length} vote buttons`);
}

function handleCorrectTick(e) {
    const container = e.currentTarget.closest('.question__answer');
    const correctTick = e.currentTarget;
    const objectId = container.dataset.contentId;

    const initial_isCorrect = correctTick.classList.contains('active');

    console.log('handleCorrectTick: ', objectId);

    fetch('/api/accept_answer/' + objectId + '/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({
            object_id: objectId,
        })
    })
    .then(response => {
        if (!response.ok) {
            updateTick(container, initial_isCorrect);
            if (response.status === 403) {
                throw new Error('Вы не можете одобрить ответ на чужой вопрос!');
            }
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {

        updateTick(container, data.is_correct);
    })
    .catch(error => {
        console.error('Full error details:', error);
        console.error('Error name:', error.name);
        console.error('Error message:', error.message);
        console.error('Error stack:', error.stack);

        alert(error.message);
    })
}

questionContainers.forEach(container => {
    const voteButtons = container.querySelectorAll('.vote-btn');
    voteButtons.forEach(button => {
        button.addEventListener('click', handleVote);
    });
});

answerContainers.forEach(container => {
    const correctTick = container.querySelector('.correct-tick');
    if (correctTick) {
        correctTick.addEventListener('click', handleCorrectTick);
    }
});

document.addEventListener('DOMContentLoaded', function() {
    initializeUserVotes();
    initializeVoteSystem();
});