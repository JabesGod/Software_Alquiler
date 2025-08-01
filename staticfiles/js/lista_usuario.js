$(document).ready(function() {
    // Initialize tooltips
    $('[title]').tooltip({
        trigger: 'hover',
        placement: 'top',
        container: 'body'
    });
    
    // Handle filter changes
    $('#estadoFilter, #rolFilter').change(function() {
        $(this).closest('form').submit();
    });
    
    // Add a subtle animation when hovering over table rows
    $('.users-table tbody tr').hover(
        function() {
            $(this).css('transform', 'translateX(2px)');
        },
        function() {
            $(this).css('transform', 'translateX(0)');
        }
    );
    
    // Make action buttons slightly larger on hover
    $('.action-button').hover(
        function() {
            $(this).css('transform', 'scale(1.1)');
        },
        function() {
            $(this).css('transform', 'scale(1)');
        }
    );
    
    // Add confirmation dialog for delete actions
    $('.action-button.delete').click(function(e) {
        if (!confirm('¿Estás seguro que deseas eliminar este usuario?')) {
            e.preventDefault();
            return false;
        }
    });
});
