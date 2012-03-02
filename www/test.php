<?php

include dirname(__FILE__) . '/../include/common.php';

$time = 0;
$id = 0;
if (isset($_GET['id']))
{
	if (isset($_GET['time']) && is_numeric($_GET['time']))
	{
		$id = intval($_GET['id']);
		$time = intval($_GET['time']);
	}
	else
		$id = sanitize_hash($_GET['id']);
}
else
{
	header('Location: /');
	die;
}

$t = new Template('site');
$t->testId = $id;
$t->time = $time;
$t->render('view-test');
?>
