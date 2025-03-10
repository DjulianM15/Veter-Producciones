// Evento de envío del formulario
$('#eventForm').submit(function(event) {
    event.preventDefault();
    const date = $('#eventDate').val();
    const time = $('#eventTime').val();
    const description = $('#eventDescription').val();
    const eventItem = `<li class="list-group-item"><strong>${date} ${time}</strong>: ${description}</li>`;
    $('#eventList').append(eventItem);
    this.reset();
});