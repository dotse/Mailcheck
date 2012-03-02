<?php
/**
 * To enable maintenance mode:
 * 1. Replace index.php with this file or include this file with exit(); after at the top of index.php
 * 2. Make sure this rewrite is always selected first: RewriteRule !\.(js|ico|gif|jpg|png|css|swf|txt)$ index.php
 * 3. Reload apache
 * 4. Fix problems on the site!
 */

require_once dirname(__FILE__) . '/../include/common.php';

$view = new Template('site');
$view->render('maintenance');
?>
