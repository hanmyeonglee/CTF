<?php
	header('Content-Type: text/css');

	$whatUwant = $_GET['whatUwant'] ?? 'whatUwant';
	$secret = $_SERVER['REMOTE_ADDR'] === '127.0.0.1' ? file_get_contents('/secret') : 'secret';
	if (strlen($whatUwant) < 10)
		echo $whatUwant . $secret;
?>