<div class="breadcrumb">
	<a href="/admin">Admin</a> > Schedule list
</div>

<table>
	<th>Domain</th>
	<th>Start time</th>
	<th>&nbsp;</th>

<?php if (count($this->list) > 0): ?>
<?php foreach($this->list as $l): ?>
	<tr>
		<td><?=$l['domain']?></td>
		<td><?=$l['start_time']?></td>
		<td>
			<a href="/admin/schedule.php?delete=<?=$l['id']?>" onclick="return confirm('Are you sure?');">Delete</a>
		</td>
	</tr>
<?php endforeach; ?>
<?php else: ?>
	<tr><td colspan="3">No scheduled tests available</td></tr>
<?php endif; ?>
</table>
<a href="/admin/schedule.php?new">Schedule new</a>
