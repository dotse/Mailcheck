<?php

require_once dirname(__FILE__) . '/../../include/common.php';
require_once dirname(__FILE__) . '/../../include/admin.php';

adminsOnly();


$view = new Template('admin/layout.php');

//
// LIST
//
if (isset($_GET['list']))
{
	$result = Database::query('SELECT * FROM frequency ORDER BY domain ASC');
	
	$view->list = $result;
	$view->render('admin/frequency_list.php');
}
//
// EDIT 
//
else if (isset($_POST['save_edit']))
{
	$unit = $_POST['unit'];
	$interval = intval($_POST['interval']);
	$interval = unitToSeconds($unit) > 0 ? $interval * unitToSeconds($unit) : $interval;
		

// TODO: THIS NEEDS CLEANING
	$data = array($_POST['domain'], $_POST['max_tests'], $interval, $_POST["description"], $_POST['id']);
	Database::query("UPDATE frequency SET domain=?, max_tests=?,interval=?,description=? WHERE id=?", $data);
	
	header('Location: /admin/frequency.php?list');
	exit();
}
else if (isset($_GET['edit']))
{
	$id = intval($_GET['edit']);
	
	$row = Database::query('SELECT * FROM frequency WHERE id = ?', array($id));
	
	if (is_array($row))
		$view->row = $row[0];
	$view->render('admin/frequency_form');
}
//
// NEW
//
else if (isset($_GET['new']))
{
	if ($_GET['new'] == 'blacklist')
		$view->row = array('domain' => '', 'max_tests' => '0', 'interval' => '0', 'id' => '');
	else
		$view->row = array('domain' => '', 'max_tests' => '', 'interval' => '', 'id' => '');
	$view->render('admin/frequency_form');
}
else if (isset($_POST['save_new']))
{
	$unit = $_POST['unit'];
	$interval = intval($_POST['interval']);
	$interval = unitToSeconds($unit) > 0 ? $interval * unitToSeconds($unit) : $interval;
	
	$data = array($_POST['domain'], $_POST['max_tests'], $interval);
	Database::query("INSERT INTO frequency (domain,max_tests,interval) VALUES(?,?,?)", $data);
	
	header('Location: /admin/frequency.php?list');
	exit();
}
//
// DELETE
//
else if (isset($_GET['delete']))
{
	$id  = intval($_GET['delete']);
	Database::query("DELETE FROM frequency WHERE id = ?", array($id));
	
	header('Location: /admin/frequency.php?list');
	exit();
}


?>
