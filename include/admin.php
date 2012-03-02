<?php

session_start();

function login($username, $password)
{
	// TODO: this should be done a bit better
	$password = md5($username . $password);
	if ($username == 'mailcheck' && $password == '9095b11649b94ee63a4c0c1cf9678fda')
	{
		$_SESSION['user'] = $username;
		return true;
	}
	
	return false;
}


function logout()
{
	unset($_SESSION['user']);
}


function isLoggedIn()
{
	if (isset($_SESSION['user']))
	{
		return true;
	}
	
	return false;
}

function adminsOnly()
{
	if (isLoggedIn() == false)
	{
		header('Location: /admin?login');
		exit();
	}
		
}
?>
