<div class="breadcrumb">
	<a href="/admin">Admin</a> > IP frequency list
</div>

<table>
	<th>IP</th>
	<th>Max tests</th>
	<th>Interval</th>
	<th>&nbsp;</th>
<?php 
$i="#ffffff";
foreach($this->list as $l): 
  if ($i == "#ffffff") {$i="#e0e0e0";} else {$i="#ffffff";}
?>
	<tr style='background: <?=$i?>'>
		<td><?=$l['ip']?></td>
		<td><?=$l['max_tests']?></td>
		<?php if ($l['interval'] > 0): ?>
		<td><?php $v = autoFormatSeconds($l['interval']); echo $v[1] . ' ' . $v[0]?></td>
		<?php else: ?>
		<td><?=$l['interval']?></td>
		<?php endif; ?>
		<td>
			<a href="/admin/ip-frequency.php?edit=<?=$l['id']?>">Edit</a> - 
			<a href="/admin/ip-frequency.php?delete=<?=$l['id']?>" onclick="return confirm('Are you sure?');">Delete</a>
		</td>
	</tr>
<?php endforeach; ?>
</table>
<a href="/admin/ip-frequency?new">Add new</a>
