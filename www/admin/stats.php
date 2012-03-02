<?php

require_once dirname(__FILE__) . '/../../include/common.php';
require_once dirname(__FILE__) . '/../../include/admin.php';

adminsOnly();

$limit = 5;

$view = new Template('admin/layout.php');

$request = Request::getCurrentRequest();

$year = $month = null;
$time_interval = $time_where = '';
if (isset($_POST['year']) || isset($_POST['year']))
{
	$year = $request->POST('year', 'int', 0);
	$month = $request->POST('month', 'int', 0);

	// If only month is selected, 
	if ($year == 0 && $month != 0)
		$year = date('Y', time());

	$start = "$year-".str_pad($month, 2, '0', STR_PAD_LEFT)."-01";
	$end = date('Y-m-d', strtotime("$start + 1 month - 1 day"));

	// No year chosen == all years
	if ($year == 0)
		$start = $end = '';
	// Only year selected = all months this year
	if ($year != 0 && $month == 0)
	{
		$start = "$year-01-01";
		$end = '';
	}

	$time_interval = array();
	if ($start != '')
		$time_interval[] = "t.finished >= '$start'::timestamp";
	if ($end != '')
		$time_interval[] = "t.finished <= '$end'::timestamp";

	$time_interval = implode(' AND ', $time_interval);
	if ($time_interval != '')
	{
		$time_where = " WHERE (" . $time_interval . ")";
		$time_interval = " AND (" . $time_interval . ")";
	}
}

//
$view->interval = "$start - $end";
$view->year = $year != null ? intval($year) : null;
$view->month = $month != null ? intval($month) : null;

$yesterday = date('Y-m-d 00:00', strtotime('now - 1 day'));
$today = date('Y-m-d 00:00', strtotime('now'));

$total = Database::query("select 
	(select count(t.id) from test t where t.finished is not null $time_interval) as totaltest,
	--(select count(t.id) from test t where t.finished is not null ". ($time_interval=='' ? "and t.started > now() - interval '30 days'" : $time_interval).") as lastthirtydays,
	(select count(distinct t.\"domain\") from test t where t.finished is not null $time_interval) as totaldomains,
	(select count(distinct pr.test_id) from plugin_result pr, test t where pr.\"name\" = 'goldstar' AND t.id = pr.test_id $time_interval) as testswithgold,
	(select sum(pr.value_numeric) from plugin_result pr, test t WHERE pr.\"name\" = 'goldstar' AND t.id = pr.test_id $time_interval) as totalgold
	");

$total = array_shift($total);
$view->totalTests = intval($total['totaltest']);
//$view->avgTestPerDay = round($total['lastthirtydays'] / 30.0, 2);
$view->totalDomains = intval($total['totaldomains']);
$view->totalWithGold = intval($total['testswithgold']);
$view->totalGold = intval($total['totalgold']);
if ($total['totaltest'] > 0)
{
	$view->goldPerTest = round($total['totalgold'] / $total['totaltest'], 4);
	$view->totalWithGoldPercent = round(($total['testswithgold'] / $total['totaltest'])*100, 2);
}
else
{	$view->goldPerTest = 0;
	$view->totalWithGoldPercent = 0;
}
$view->plugin_per_test = $total['plugin_per_test'];

$totalX = Database::query("select
	(select avg((select count(id) from plugin p where p.test_id = t.id $time_interval)) from test t where t.finished is not null) as total,
	(select avg((select count(id) from plugin p where p.test_id = t.id AND p.status = 1 $time_interval)) from test t where t.finished is not null) as ok,
	(select avg((select count(id) from plugin p where p.test_id = t.id AND p.status = 2 $time_interval)) from test t where t.finished is not null) as warning,
	(select avg((select count(id) from plugin p where p.test_id = t.id AND p.status = 3 $time_interval)) from test t where t.finished is not null) as error
	");
$totalX = array_shift($totalX);
$view->totalPerTest = round($totalX['total'], 2);
$view->totalOkPerTest = round($totalX['ok'], 2);
$view->totalWarningPerTest = round($totalX['warning'], 2);
$view->totalErrorPerTest = round($totalX['error'], 2);


// Totals about plugin results
$totalResults = Database::query("select
	(select count(p.test_id) from plugin p, test t where p.status = 1 AND t.id = p.test_id $time_interval) as ok,
	(select count(p.test_id) from plugin p, test t where p.status = 2 AND t.id = p.test_id $time_interval) as warning,
	(select count(p.test_id) from plugin p, test t where p.status = 3 AND t.id = p.test_id $time_interval) as error,
	(select count(p.test_id) from plugin p, test t where p.status in (1,2,3) AND t.id = p.test_id $time_interval) as total
	");
$totalResults = array_shift($totalResults);
$view->totalOk = $totalResults['ok'];
$view->totalWarning = $totalResults['warning'];
$view->totalError = $totalResults['error'];


// Top X tested sites
$topTested = Database::query("select count(t.id), t.\"domain\" from test t where t.finished is not null $time_interval group by t.\"domain\" order by count desc limit ". $limit);
$view->topTested = $topTested;

// Top X testers
$topTesters = Database::query("select count(t.id), t.\"email\" from test t where t.finished is not null $time_interval group by t.\"email\" order by count desc limit ". $limit);
$view->topTesters = $topTesters;

// Top X most common warnings and errors
$topPluginWarning = Database::query("select count(p.plugin) as count, p.plugin from plugin p, test t where p.status = 2 AND t.id = p.test_id $time_interval group by p.plugin order by count desc limit " . $limit);
$view->topPluginWarning = $topPluginWarning;
$topPluginError = Database::query("select count(p.plugin) as count, p.plugin from plugin p, test t where p.status = 3 AND t.id = p.test_id $time_interval group by p.plugin order by count desc limit " . $limit);
$view->topPluginError = $topPluginError;



$view->months = array("January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December");

$view->render('admin/stats.php');
?>
