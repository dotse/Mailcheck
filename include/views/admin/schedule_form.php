<div class="breadcrumb">
	<a href="/admin">Admin</a> > <a href="/admin/schedule.php?list">Schedule list</a> > Schedule test
</div>

<form method="post" action="/admin/schedule.php">
	<div class="admin-form">
		<label>Domain:</label>
		<div>
			<input type="text" name="domain" />
		</div>

		<label>Start time (ex 2009-07-07 10:10:10):</label>
		<div>
			<input type="text" name="start_time" value="<?=date('Y-m-d H:i:s', time())?>" />
		</div>

		<div>
			<input type="submit" name="save" value="Save" />
		</div>
	</div>
</form>
