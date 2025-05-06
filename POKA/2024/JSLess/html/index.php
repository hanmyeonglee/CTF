<?php
	header('Content-Type: text/plain');
	
	$name = $_GET['name'] ?? 'alice';
	if (strlen($name) < 70)
		echo "Hello, [$name].";
?>