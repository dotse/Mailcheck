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
	$result = Database::query('SELECT * FROM bug_report ORDER BY created DESC');
	
	foreach ($result as $k => $r)
	{
		$result[$k]['description'] = strlen($r['description']) > 100 ? substr($r['description'], 0, 100).'...' : $r['description'];
	}
	
	
	$view->list = $result;
	$view->render('admin/bugreports_list.php');
}
//
// VIEW 
//
else if (isset($_GET['view']))
{
	$id = intval($_GET['id']);
	$result = Database::query('SELECT * FROM bug_report WHERE id = ? LIMIT 1', array($id));
	$result[0]['email'] = $result[0]['email'] == '' ? 'Anonymous' : $result[0]['email'];
	$view->report = $result[0];
	
	$view->render('admin/bugreports_view.php');
}
?>
