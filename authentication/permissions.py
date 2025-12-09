from rest_framework import permissions


class IsVerified(permissions.BasePermission):
    """Permission to check if user email is verified"""
    
    message = "Email verification required."
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_verified


class IsAdmin(permissions.BasePermission):
    """Permission for Admin role only"""
    
    message = "Admin access required."
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'ADMIN'
    
    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and request.user.role == 'ADMIN'


class IsFM(permissions.BasePermission):
    """Permission for Facility Manager role only"""
    
    message = "Facility Manager access required."
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'FM'
    
    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and request.user.role == 'FM'


class IsContractor(permissions.BasePermission):
    """Permission for Contractor role only"""
    
    message = "Contractor access required."
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'CONTRACTOR'
    
    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and request.user.role == 'CONTRACTOR'


class IsCustomer(permissions.BasePermission):
    """Permission for Customer role only"""
    
    message = "Customer access required."
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'CUSTOMER'
    
    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and request.user.role == 'CUSTOMER'


class IsInvestor(permissions.BasePermission):
    """Permission for Investor role only"""
    
    message = "Investor access required."
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'INVESTOR'
    
    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and request.user.role == 'INVESTOR'


class IsAdminOrFM(permissions.BasePermission):
    """Permission for Admin or Facility Manager roles"""
    
    message = "Admin or Facility Manager access required."
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['ADMIN', 'FM']
    
    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and request.user.role in ['ADMIN', 'FM']


class IsOwnerOrAdmin(permissions.BasePermission):
    """Permission for object owner or admin"""
    
    message = "You must be the owner or an admin to perform this action."
    
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        
        # Admin has full access
        if request.user.role == 'ADMIN':
            return True
        
        # Check if user is the owner
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'owner'):
            return obj.owner == request.user
        elif isinstance(obj, request.user.__class__):
            return obj == request.user
        
        return False


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Permission for owner to edit, others can only read"""
    
    def has_object_permission(self, request, view, obj):
        # Read permissions for any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions only for owner
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'owner'):
            return obj.owner == request.user
        elif isinstance(obj, request.user.__class__):
            return obj == request.user
        
        return False


class RoleBasedPermission(permissions.BasePermission):
    """
    Dynamic role-based permission class.
    Usage: permission_classes = [RoleBasedPermission]
    Add allowed_roles attribute to view: allowed_roles = ['ADMIN', 'FM']
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        allowed_roles = getattr(view, 'allowed_roles', None)
        if allowed_roles is None:
            return True
        
        return request.user.role in allowed_roles
