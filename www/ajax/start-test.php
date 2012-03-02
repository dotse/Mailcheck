<?php

include_once '../../include/common.php';
include_once '../../include/tests.php';

$request = Request::getCurrentRequest();
$extra = $request->POST('extra', 'string');
$extra = ''; // Disabled the extra paramters feature for now
$email = $request->POST('email', 'email');
if (filter_var($email, FILTER_VALIDATE_EMAIL) === false)
{
	echo json_encode(array('state' => 'INVALID_EMAIL'));
	die;
}

$result = array();
$email = isset($_POST['email']) ? $_POST['email'] : '';
$domain = $email;
if (strpos($email, '@') !== false)
{
	$domain = explode('@', $email, 2);
	$domain = $domain[1];
}
else
{
	$result['error'] = 1;
}

// Check if we are supposed to run slow tests
$runSlowTests = 'f';
if (isset($_POST['slow-tests']) && $_POST['slow-tests'] == 'true')
	$runSlowTests = 't';

//
// START A NEW TEST
//

$result = array();
$allowed = isAllowedToStart($domain);
if ($allowed === true && $domain != '')
{
	$test = Database::query("INSERT INTO queue (domain, email, test_id, ip, extra, waiting_input, slow) VALUES(?, ?, nextval('test_id_seq'), ?, ?, ?, ?)
		RETURNING test_id, extract(epoch from start_time)::integer as start_time", array($domain, $email, $_SERVER['REMOTE_ADDR'], $extra, $runSlowTests, $runSlowTests));
	$testId = $test[0]['test_id'];
	$time = $test[0]['start_time'];

	if ($runSlowTests == 't')
		$result = array('state' => 'WAITING_INPUT', 'domain' => $domain, 'test_id' => $testId, 'start_time' => $time, 'emails' => Config::get('emailAddresses'), 'outlookEmails' => Config::get('outlookEmailAddresses'));
	else
		$result = array('state' => 'QUEUED', 'domain' => $domain, 'test_id' => $testId, 'start_time' => $time);
}
else
{
	list($message, $customMessage) = $allowed;

	if ($customMessage == false)
		$message = translate($message);
	$result = array('state' => 'DENIED', 'domain' => $domain, 'test_id' => $testId, 'message' => $message, 'custom' => $customMessage);
}


echo json_encode($result);
?>
