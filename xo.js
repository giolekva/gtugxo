(function() {
	function InitServerConnection(token) {
		var channel = new goog.appengine.Channel(token);
		var socket = channel.open();
		socket.onopen = function() {
			console.log('opened');
		};
		socket.onmessage = function(msg) {
			var data = $.parseJSON(msg.data);
			if (data.move) {
				var index = 3 * data.move.x + data.move.y;
				console.log(index);
				$('#board td:eq(' + index + ')')
					.css('background', 'blue');
			}
		};
	}

	$(function() {
		InitServerConnection(channel_token);
		
		$('#board td').click(function() {
			var cell = $(this);
			var y = cell.parent().children().index(cell);
			var x = cell.parent().parent()
				.children().index(cell.parent());

			$.ajax({
				url: '/move',
				data: {
					'id': board_id,
					'player_id': player_id,
					'x': x,
					'y': y},
			}).done(function(data) {
				cell.css('background', 'red');
				data = $.parseJSON(data);
				console.log(data.winner);
				console.log(player_id);
			});
		});
	});
})();
