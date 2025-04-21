// Timer variables
let timerInterval;
let timerRunning = false;
let isPaused = false;
let totalSeconds = 0;
let currentSeconds = 0;
let isRestPhase = false;
let exerciseDuration = 0;
let restDuration = 0;
let exerciseId = 0;
let exerciseName = '';

// Elements
const timerModal = new bootstrap.Modal(document.getElementById('timerModal'));
const timerMinutes = document.getElementById('timerMinutes');
const timerSeconds = document.getElementById('timerSeconds');
const timerProgress = document.getElementById('timerProgress');
const timerPhase = document.getElementById('timerPhase');
const timerStatus = document.getElementById('timerStatus');
const exerciseNameElem = document.getElementById('exerciseName');
const pauseTimerBtn = document.getElementById('pauseTimer');
const resetTimerBtn = document.getElementById('resetTimer');

// Initialize timer buttons
if (pauseTimerBtn) {
    pauseTimerBtn.addEventListener('click', togglePause);
}

if (resetTimerBtn) {
    resetTimerBtn.addEventListener('click', resetTimer);
}

/**
 * Start the exercise timer
 * @param {number} id - Exercise ID
 * @param {string} name - Exercise name
 * @param {number} duration - Exercise duration in seconds
 * @param {number} rest - Rest duration in seconds
 */
function startTimer(id, name, duration, rest) {
    // Reset any running timer
    clearInterval(timerInterval);
    
    // Set timer variables
    exerciseId = id;
    exerciseName = name;
    exerciseDuration = duration;
    restDuration = rest;
    totalSeconds = duration;
    currentSeconds = duration;
    isRestPhase = false;
    timerRunning = true;
    isPaused = false;
    
    // Update UI
    updateTimerDisplay(currentSeconds);
    timerPhase.textContent = 'Ejercicio';
    timerPhase.style.backgroundColor = 'rgba(255, 107, 53, 0.1)'; // Primary color light
    exerciseNameElem.textContent = name;
    
    // Show modal
    timerModal.show();
    
    // Play start sound
    playSound('start');
    
    // Start countdown
    timerInterval = setInterval(updateTimer, 1000);
    updateTimerDisplay(currentSeconds);
}

/**
 * Update timer countdown each second
 */
function updateTimer() {
    if (isPaused) return;
    
    currentSeconds--;
    
    // Update UI
    updateTimerDisplay(currentSeconds);
    
    // Update progress bar
    const progressPercentage = isRestPhase 
        ? ((restDuration - currentSeconds) / restDuration) * 100
        : ((exerciseDuration - currentSeconds) / exerciseDuration) * 100;
    
    timerProgress.style.width = `${progressPercentage}%`;
    
    // Check if time's up
    if (currentSeconds <= 0) {
        // If we were in exercise phase, switch to rest
        if (!isRestPhase) {
            playSound('rest');
            isRestPhase = true;
            totalSeconds = restDuration;
            currentSeconds = restDuration;
            timerPhase.textContent = 'Descanso';
            timerPhase.style.backgroundColor = 'rgba(23, 162, 184, 0.1)'; // Info color light
            timerProgress.classList.remove('bg-primary');
            timerProgress.classList.add('bg-info');
        } else {
            // End of both exercise and rest
            playSound('complete');
            clearInterval(timerInterval);
            timerRunning = false;
            timerPhase.textContent = '¡Completado!';
            timerPhase.style.backgroundColor = 'rgba(40, 167, 69, 0.1)'; // Success color light
        }
    }
}

/**
 * Update the timer display with the current time
 * @param {number} seconds - Current time in seconds
 */
function updateTimerDisplay(seconds) {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    
    timerMinutes.textContent = minutes.toString().padStart(2, '0');
    timerSeconds.textContent = remainingSeconds.toString().padStart(2, '0');
}

/**
 * Toggle pause/resume of the timer
 */
function togglePause() {
    if (!timerRunning) return;
    
    isPaused = !isPaused;
    pauseTimerBtn.innerHTML = isPaused 
        ? '<i class="fas fa-play me-1"></i> Reanudar'
        : '<i class="fas fa-pause me-1"></i> Pausar';
}

/**
 * Reset the timer to start again
 */
function resetTimer() {
    if (!timerRunning) {
        // Start a new timer with the same exercise
        startTimer(exerciseId, exerciseName, exerciseDuration, restDuration);
        return;
    }
    
    // Reset to exercise phase
    clearInterval(timerInterval);
    isRestPhase = false;
    totalSeconds = exerciseDuration;
    currentSeconds = exerciseDuration;
    isPaused = false;
    
    // Update UI
    timerPhase.textContent = 'Ejercicio';
    timerPhase.style.backgroundColor = 'rgba(255, 107, 53, 0.1)';
    timerProgress.style.width = '0%';
    timerProgress.classList.remove('bg-info');
    timerProgress.classList.add('bg-primary');
    pauseTimerBtn.innerHTML = '<i class="fas fa-pause me-1"></i> Pausar';
    
    // Restart timer
    updateTimerDisplay(currentSeconds);
    timerInterval = setInterval(updateTimer, 1000);
}

/**
 * Play sound for timer events
 * @param {string} soundType - Type of sound to play (start, rest, complete)
 */
function playSound(soundType) {
    let frequency, duration;
    
    switch(soundType) {
        case 'start':
            frequency = 800;
            duration = 200;
            break;
        case 'rest':
            frequency = 600;
            duration = 300;
            break;
        case 'complete':
            frequency = 1000;
            duration = 500;
            break;
        default:
            frequency = 500;
            duration = 100;
    }
    
    try {
        // Create audio context
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);
        
        oscillator.type = 'sine';
        oscillator.frequency.value = frequency;
        gainNode.gain.value = 0.5;
        
        oscillator.start();
        
        setTimeout(() => {
            oscillator.stop();
        }, duration);
    } catch (e) {
        console.log('Audio not supported or blocked by browser policy');
    }
}
