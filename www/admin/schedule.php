<?php

require_once dirname(__FILE__) . '/../../include/common.php';
require_once dirname(__FILE__) . '/../../include/admin.php';

adminsOnly();


$view = new Template('admin/layout.php');

//
// List
//
if (isset($_GET['list']))
{
	$result = Database::query("SELECT * FROM queue WHERE start_time >= now() + interval '10 seconds' ORDER BY start_time ASC");
	
	if (!is_array($result))
		$result = array();

	$view->list = $result;
	$view->render('admin/schedule_list.php');
}
else if (isset($_GET['delete']))
{
	$id = intval($_GET['delete']);
	
	Database::query('DELETE FROM queue WHERE id = ?', array($id));
	header('Location: /admin/schedule.php?list');
	die;
}


//
// NEW
//
else if (isset($_GET['new']))
{
	$view->render('admin/schedule_form.php');
}
else if (isset($_POST['save']))
{
	$domain = $_POST['domain'];
	$time = $_POST['start_time'];

	Database::query('INSERT INTO queue (domain, start_time, test_id) VALUES(?, ?, nextval(\'test_id_seq\'))', array($domain, $time));
	header('Location: /admin/schedule.php?list');
	die;
}

?>
