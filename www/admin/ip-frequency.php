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
	$result = Database::query('SELECT * FROM frequency_ip ORDER BY ip ASC');
	
	$view->list = $result;
	$view->render('admin/ip_frequency_list.php');
}
//
// EDIT 
//
else if (isset($_POST['save_edit']))
{
	$unit = $_POST['unit'];
	$interval = intval($_POST['interval']);
	$interval = unitToSeconds($unit) > 0 ? $interval * unitToSeconds($unit) : $interval;
		
	$data = array($_POST['ip'], $_POST['max_tests'], $interval, $_POST['id']);
	Database::query("UPDATE frequency_ip SET ip=?, max_tests=?,interval=? WHERE id=?", $data);
	
	header('Location: /admin/ip-frequency.php?list');
	exit();
}
else if (isset($_GET['edit']))
{
	$id = intval($_GET['edit']);
	
	$row = Database::query('SELECT * FROM frequency_ip WHERE id = ?', array($id));
	
	if (is_array($row))
		$view->row = $row[0];
	$view->render('admin/ip_frequency_form');
}
//
// NEW
//
else if (isset($_GET['new']))
{
	$view->row = array('ip' => '', 'max_tests' => '0', 'interval' => '0', 'id' => '');
	$view->render('admin/ip_frequency_form');
}
else if (isset($_POST['save_new']))
{
	$unit = $_POST['unit'];
	$interval = intval($_POST['interval']);
	$interval = unitToSeconds($unit) > 0 ? $interval * unitToSeconds($unit) : $interval;
	
	$data = array($_POST['ip'], $_POST['max_tests'], $interval);
	Database::query("INSERT INTO frequency_ip (ip,max_tests,interval) VALUES(?,?,?)", $data);
	
	header('Location: /admin/ip-frequency.php?list');
	exit();
}
//
// DELETE
//
else if (isset($_GET['delete']))
{
	$id  = intval($_GET['delete']);
	Database::query("DELETE FROM frequency_ip WHERE id = ?", array($id));
	
	header('Location: /admin/ip-frequency.php?list');
	exit();
}


?>
