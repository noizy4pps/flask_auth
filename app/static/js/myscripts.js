

$(function () {
  $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            const csrf_token = $('meta[name="csrf-token"]').attr('content');
            if (csrf_token) {
                xhr.setRequestHeader("X-CSRFToken", csrf_token);
            }
        }
    });
  $('.toggle-setting').on('change', function () {
    const settingId = $(this).data('id');
    const newValue = $(this).is(':checked');
    
    $.ajax({
      url: 'gsettings',  // make sure to match your Flask route
      method: 'POST',
      contentType: 'application/json',
      data: JSON.stringify({ id: settingId, value: newValue }),
      success: function (res) {
        console.log(res.message);
      },
      error: function (err) {
        alert('Error toggling setting');
      }
    });
  });
});

document.addEventListener('DOMContentLoaded', function () {
            document.querySelectorAll('.toggle-desc').forEach(link => {
            link.addEventListener('click', function (e) {
                e.preventDefault();
                const cell = this.closest('.desc-cell');
                const full = cell.getAttribute('data-full');
                const short = cell.getAttribute('data-short');
                const isFull = cell.textContent.includes(full);

                if (isFull) {
                cell.innerHTML = `${short}... <a href="#" class="toggle-desc">[more]</a>`;
                } else {
                cell.innerHTML = `${full} <a href="#" class="toggle-desc">[less]</a>`;
                }
            });
            });
        });