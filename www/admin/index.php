<?php
require_once dirname(__FILE__) . '/../../include/common.php';
require_once dirname(__FILE__) . '/../../include/admin.php';

$v = new Template('admin/layout');

if (isset($_POST['login']))
{
	$login = login($_POST['username'], $_POST['password']);
	if ($login == false)
		$v->render('admin/login');
	else
		$v->render('admin/index');
		
}
else if (isset($_GET['login']))
{
	$v->render('admin/login');
}
else if (isset($_GET['logout']))
{
	adminsOnly();
	logout();
	header('Location: /admin?login');
}
else
{
	adminsOnly();
	$v->render('admin/index');
}

?>