// HR Interview JavaScript

$(document).ready(function() {
    let selectedQuestion = '';
    let mediaRecorder;
    let audioChunks = [];
    let recordingTimer;
    let recordingSeconds = 0;

    // Question selection
    $('.question-item').click(function() {
        selectedQuestion = $(this).data('question');
        $('#selectedQuestion').text(selectedQuestion);
        $('#answerSection').show();
        
        // Reset answer inputs
        $('#textAnswer').val('');
        $('#audioPlayback').attr('src', '').hide();
        $('#submitAudioAnswer').hide();
        
        // Scroll to answer section
        $('html, body').animate({
            scrollTop: $('#answerSection').offset().top - 100
        }, 500);
    });

    // Answer type selection
    $('#textAnswerBtn').click(function() {
        $('#textAnswerDiv').show();
        $('#audioAnswerDiv').hide();
    });

    $('#audioAnswerBtn').click(function() {
        $('#textAnswerDiv').hide();
        $('#audioAnswerDiv').show();
    });

    // Text answer submission
    $('#submitTextAnswer').click(function() {
        const answer = $('#textAnswer').val();
        
        if (!answer.trim()) {
            showNotification('Please provide an answer', 'warning');
            return;
        }
        
        $('#loadingModal').modal('show');
        
        apiCall('/interview/api/analyze-answer/', 'POST', {
            question: selectedQuestion,
            answer: answer,
            type: 'hr',
            is_audio: false
        })
        .done(function(response) {
            $('#loadingModal').modal('hide');
            cleanupModals();
            
            if (response.success) {
                $('#feedbackContent').html(formatFeedback(response.feedback));
                $('#feedbackSection').show();
                
                // Show follow-up question if provided
                if (response.follow_up) {
                    $('#followUpQuestion').text(response.follow_up);
                    $('#followUpSection').show();
                }
                
                $('html, body').animate({
                    scrollTop: $('#feedbackSection').offset().top - 100
                }, 500);
            }
        })
        .fail(function(xhr, status, error) {
            console.error('HR text answer analysis error:', status, error);
            $('#loadingModal').modal('hide');
            cleanupModals();
            showNotification('Error analyzing answer. Please try again.', 'danger');
        });
    });

    // Audio recording with timer
    $('#recordBtn').click(async function() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);
            audioChunks = [];
            recordingSeconds = 0;
            
            mediaRecorder.ondataavailable = event => {
                audioChunks.push(event.data);
            };
            
            mediaRecorder.onstop = () => {
                const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                const audioUrl = URL.createObjectURL(audioBlob);
                $('#audioPlayback').attr('src', audioUrl).show();
                $('#submitAudioAnswer').show();
                clearInterval(recordingTimer);
                $('.recording-time').hide();
            };
            
            mediaRecorder.start();
            $(this).hide();
            $('#stopBtn').show();
            $('.recording-time').show();
            
            // Start timer
            recordingTimer = setInterval(() => {
                recordingSeconds++;
                const minutes = Math.floor(recordingSeconds / 60);
                const seconds = recordingSeconds % 60;
                $('#recordingTime').text(
                    `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
                );
            }, 1000);
            
            showNotification('Recording started. Speak clearly!', 'info');
        } catch (err) {
            showNotification('Error accessing microphone', 'danger');
        }
    });

    $('#stopBtn').click(function() {
        if (mediaRecorder && mediaRecorder.state !== 'inactive') {
            mediaRecorder.stop();
            mediaRecorder.stream.getTracks().forEach(track => track.stop());
            $(this).hide();
            $('#recordBtn').show();
        }
    });

    // Submit audio answer
    $('#submitAudioAnswer').click(function() {
        const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
        const formData = new FormData();
        formData.append('audio', audioBlob, 'answer.wav');
        formData.append('question', selectedQuestion);
        formData.append('type', 'hr');
        
        $('#loadingModal').modal('show');
        
        $.ajax({
            url: '/interview/api/save-audio/',
            method: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            timeout: 30000, // 30 second timeout for audio upload
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .done(function(response) {
            $('#loadingModal').modal('hide');
            cleanupModals();
            
            if (response.success) {
                $('#feedbackContent').html(formatFeedback(response.feedback));
                $('#feedbackSection').show();
                
                // Show follow-up question if provided
                if (response.follow_up) {
                    $('#followUpQuestion').text(response.follow_up);
                    $('#followUpSection').show();
                }
                
                $('html, body').animate({
                    scrollTop: $('#feedbackSection').offset().top - 100
                }, 500);
            }
        })
        .fail(function(xhr, status, error) {
            console.error('HR audio submission error:', status, error);
            $('#loadingModal').modal('hide');
            cleanupModals();
            
            if (status === 'timeout') {
                showNotification('Audio upload timed out. Please try again.', 'danger');
            } else {
                showNotification('Error submitting audio. Please try again.', 'danger');
            }
        });
    });

    // Answer follow-up question
    $('#answerFollowUp').click(function() {
        selectedQuestion = $('#followUpQuestion').text();
        $('#selectedQuestion').text(selectedQuestion);
        $('#followUpSection').hide();
        $('#feedbackSection').hide();
        
        // Reset answer inputs
        $('#textAnswer').val('');
        $('#audioPlayback').attr('src', '').hide();
        $('#submitAudioAnswer').hide();
        
        $('html, body').animate({
            scrollTop: $('#answerSection').offset().top - 100
        }, 500);
    });
    
    // Function to clean up modal issues
    function cleanupModals() {
        // Remove any lingering modal backdrops
        $('.modal-backdrop').remove();
        $('body').removeClass('modal-open');
        
        // Force remove the show class from loading modal
        $('#loadingModal').removeClass('show');
    }
});