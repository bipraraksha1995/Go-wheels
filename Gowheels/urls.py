from django.urls import path
from django.shortcuts import render
from django.views.generic import TemplateView
from . import views, api_views, auth_views, oauth_views, chat_views, referral_views, wishlist_views

urlpatterns = [
    # Auth API Endpoints (JWT, RBAC, MFA)
    path('api/auth/login/', auth_views.auth_login, name='auth_login'),
    path('api/auth/register/', auth_views.auth_register, name='auth_register'),
    path('api/auth/logout/', auth_views.auth_logout, name='auth_logout'),
    path('api/auth/refresh/', auth_views.auth_refresh_token, name='auth_refresh'),
    path('api/auth/me/', auth_views.auth_me, name='auth_me'),
    path('api/auth/setup-mfa/', auth_views.auth_setup_mfa, name='auth_setup_mfa'),
    path('api/auth/enable-mfa/', auth_views.auth_enable_mfa, name='auth_enable_mfa'),
    path('api/auth/verify-mfa/', auth_views.auth_verify_mfa, name='auth_verify_mfa'),
    
    # OAuth2 / SSO Endpoints
    path('oauth/login/', oauth_views.oauth_login_page, name='oauth_login'),
    path('api/auth/oauth/google/', oauth_views.oauth_google_callback, name='oauth_google_callback'),
    path('api/auth/oauth/github/', oauth_views.oauth_github_callback, name='oauth_github_callback'),
    path('oauth/success/', oauth_views.oauth_success_redirect, name='oauth_success'),
    
    # Existing URLs
    path('', views.home, name='home'),
    path('phone-check/', views.phone_check, name='phone_check'),
    path('check-phone/', views.check_phone, name='check_phone'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('super-admin-login/', views.super_admin_login, name='super_admin_login'),
    path('super-admin-panel/', views.super_admin_panel, name='super_admin_panel'),
    path('user-dashboard/', views.user_dashboard, name='user_dashboard'),
    path('user-categories/', views.user_categories, name='user_categories'),
    path('browse-vehicles/', views.browse_vehicles, name='browse_vehicles'),
    path('logout/', views.logout_view, name='logout'),
    path('super-admin-logout/', views.super_admin_logout, name='super_admin_logout'),
    path('seller-dashboard/', views.seller_dashboard, name='seller_dashboard'),
    path('seller-dashboard-form/', views.seller_dashboard_form, name='seller_dashboard_form'),
    path('get-seller-vehicles/', views.get_seller_vehicles, name='get_seller_vehicles'),
    path('super-admin-categories/', views.super_admin_categories, name='super_admin_categories'),
    path('add-brands-models-form/', views.add_brands_models_form, name='add_brands_models_form'),
    path('add-model-to-brand/', views.add_model_to_brand, name='add_model_to_brand'),
    path('api/add-brands-models/', views.add_brands_models_api, name='add_brands_models_api'),
    path('api/add-model-to-brand/', views.add_model_to_brand_api, name='add_model_to_brand_api'),
    path('update-profile/', views.update_profile, name='update_profile'),
    path('api/get-user-profile/', views.get_user_profile_api, name='get_user_profile_api'),
    path('save-admin-data/', views.save_admin_data, name='save_admin_data'),
    path('get-admin-groups/', views.get_admin_groups, name='get_admin_groups'),
    path('get-all-admin-data/', views.get_all_admin_data, name='get_all_admin_data'),
    path('user-browse-categories/', views.user_browse_categories, name='user_browse_categories'),
    path('delete-vehicle/<int:vehicle_id>/', views.delete_vehicle, name='delete_vehicle'),
    path('edit-vehicle/<int:vehicle_id>/', views.edit_vehicle, name='edit_vehicle'),
    path('toggle-vehicle-status/<int:vehicle_id>/', views.toggle_vehicle_status, name='toggle_vehicle_status'),
    path('get-vehicles/', views.get_vehicles, name='get_vehicles'),
    path('track-vehicle-click/', views.track_vehicle_click, name='track_vehicle_click'),
    path('seller-vehicles/', views.seller_vehicles, name='seller_vehicles'),
    path('seller-promote/<int:vehicle_id>/', views.seller_promote_vehicle, name='seller_promote_vehicle'),
    path('get-promotion-prices/', views.get_promotion_prices, name='get_promotion_prices'),
    path('send-otp/', views.send_otp, name='send_otp'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('test-otp/', views.test_send_otp, name='test_send_otp'),
    path('verify-otp/', views.verify_otp_view, name='verify_otp_view'),
    path('api/create-promotion/', views.create_promotion, name='create_promotion'),
    path('api/get-promotion-plans/', views.get_promotion_plans, name='get_promotion_plans'),
    path('user-sponsor/', views.user_sponsor, name='user_sponsor'),
    path('api/submit-sponsor/', views.submit_sponsor, name='submit_sponsor'),
    path('api/get-sponsor-ads/', views.get_sponsor_ads, name='get_sponsor_ads'),
    path('api/approve-sponsor/<int:sponsor_id>/', views.approve_sponsor, name='approve_sponsor'),
    path('api/reject-sponsor/<int:sponsor_id>/', views.reject_sponsor, name='reject_sponsor'),
    path('api/toggle-sponsor-status/<int:sponsor_id>/', views.toggle_sponsor_status, name='toggle_sponsor_status'),
    path('api/delete-sponsor/<int:sponsor_id>/', views.delete_sponsor, name='delete_sponsor'),
    path('api/get-active-sponsors/', views.get_active_sponsors, name='get_active_sponsors'),
    path('user-browse/', lambda request: render(request, 'user_browse.html'), name='user_browse'),
    path('seller-complete-form/', lambda request: render(request, 'seller_complete_form.html'), name='seller_complete_form'),
    path('debug-video/', lambda request: render(request, 'debug_video_upload.html'), name='debug_video'),
    path('api/delete-admin-category/', views.delete_admin_category, name='delete_admin_category'),
    path('api/delete-admin-brand/', views.delete_admin_brand, name='delete_admin_brand'),
    path('api/delete-admin-model/', views.delete_admin_model, name='delete_admin_model'),
    path('api/get-all-users/', views.get_all_users_api, name='get_all_users_api'),
    path('api/block-user/<int:user_id>/', views.block_user, name='block_user'),
    
    # Admin Ads Management URLs
    path('admin/ads/', views.admin_ads_list, name='admin_ads_list'),
    path('admin/ads/promote/<int:vehicle_id>/', views.toggle_promote, name='toggle_promote'),
    path('admin/ads/sponsor/<int:vehicle_id>/', views.toggle_sponsor, name='toggle_sponsor'),
    
    # Hierarchical Navigation URLs
    path('browse-groups/', views.browse_groups, name='browse_groups'),
    path('browse-categories/<int:group_id>/', views.browse_categories, name='browse_categories'),
    path('browse-brands/<int:category_id>/', views.browse_brands, name='browse_brands'),
    path('browse-models/<int:brand_id>/', views.browse_models, name='browse_models'),
    
    # Super Admin Management URLs
    path('super-admin-dashboard/', views.super_admin_dashboard, name='super_admin_dashboard'),
    path('manage-groups/', views.manage_groups, name='manage_groups'),
    path('manage-categories/<int:group_id>/', views.manage_categories, name='manage_categories'),
    path('manage-brands/<int:category_id>/', views.manage_brands, name='manage_brands'),
    path('manage-models/<int:brand_id>/', views.manage_models, name='manage_models'),
    path('api/delete-admin-group/', views.delete_admin_group, name='delete_admin_group'),
    
    # API URLs
    path('api/vehicles/', api_views.api_vehicles, name='api_vehicles'),
    path('api/user/<int:user_id>/', api_views.api_user_profile, name='api_user_profile'),
    
    # Chat URLs
    path('inbox/', chat_views.inbox, name='inbox'),
    path('chat/<int:chat_id>/', chat_views.chat_detail, name='chat_detail'),
    path('send-message/', chat_views.send_message, name='send_message'),
    path('get-messages/<int:chat_id>/', chat_views.get_messages, name='get_messages'),
    
    # Referral URLs
    path('referral/', referral_views.referral_page, name='referral_page'),
    path('api/apply-referral/', referral_views.apply_referral, name='apply_referral'),
    path('api/referral-stats/', referral_views.get_referral_stats, name='referral_stats'),
    
    # Wishlist URLs
    path('wishlist/', wishlist_views.wishlist_page, name='wishlist_page'),
    path('api/toggle-wishlist/', wishlist_views.toggle_wishlist, name='toggle_wishlist'),
    path('api/get-wishlist/', wishlist_views.get_wishlist, name='get_wishlist'),
    path('api/check-wishlist/', wishlist_views.check_wishlist, name='check_wishlist'),
    
    # Resale Prediction URL
    path('resale-prediction/', TemplateView.as_view(template_name='resale_prediction_full.html'), name='resale_prediction'),
]