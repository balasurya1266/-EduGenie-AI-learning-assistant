document.addEventListener('DOMContentLoaded', () => {
  const modal = document.getElementById('editModal');
  document.getElementById('editProfileBtn')?.addEventListener('click', () => modal.classList.remove('hidden'));
  document.getElementById('cancelEdit')?.addEventListener('click', () => modal.classList.add('hidden'));
  document.getElementById('saveProfile')?.addEventListener('click', async () => {
    try {
      await apiCall('/api/profile', 'PUT', {
        username: document.getElementById('editUsername').value,
        email: document.getElementById('editEmail').value
      });
      Toast.show('Profile updated!', 'success');
      setTimeout(() => location.reload(), 1000);
    } catch (err) { Toast.show(err.message, 'error'); }
  });
});
