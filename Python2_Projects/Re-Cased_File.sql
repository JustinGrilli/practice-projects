WITH

  -- subquery gets hover now information, such AS the roof estimate AND pitch estimate.
    hover_models_roof_estimates AS (
      SELECT
        hover_models_roof_estimates.id
        , hover_models_roof_estimates.estimatable_id             AS order_id
        , hover_models_roof_estimates.created_at
        , hover_models_roof_estimates.e_level_name
        , level_list_orders.level_list                           AS level_list
        , hover_models_roof_estimates.results_sq_ftg_estimate
        , COALESCE(hover_models_roof_estimates.results_pitch_estimate,
                   hover_models_roof_estimates.results_estimated_pitch,
                   hover_models_roof_estimates.results_mv_pitch) AS estimated_pitch

      FROM alooma_manowar.hover_models_roof_estimates AS hover_models_roof_estimates
        JOIN (SELECT
                estimatable_id
                , listagg(distinct e_level_name, ', ')
                  WITHIN GROUP (ORDER BY e_level_name) AS level_list
              FROM alooma_manowar.hover_models_roof_estimates
              GROUP BY estimatable_id) AS level_list_orders
          ON hover_models_roof_estimates.estimatable_id = level_list_orders.estimatable_id
      WHERE hover_models_roof_estimates.mark_for_delete IS NOT TRUE
            -- this will exclude rows that are NOT actually hover now roof estimates, but the roof area FROM the model
            AND COALESCE(hover_models_roof_estimates.results_pitch_estimate,
                         hover_models_roof_estimates.results_estimated_pitch,
                         hover_models_roof_estimates.results_mv_pitch) NOTNULL
  ),
  -- subquery gets the list of orthotag options that were selected BY the modeler.
    orthotag_list_orders AS (
      SELECT
        orders_roof_visibility_attributes.order_id
        , listagg(distinct roof_visibility_attributes.name, ', ')
          WITHIN GROUP (ORDER BY roof_visibility_attributes.name) AS orthotag_list

      FROM alooma_manowar.orders_roof_visibility_attributes AS orders_roof_visibility_attributes

        JOIN alooma_manowar.roof_visibility_attributes AS roof_visibility_attributes
          ON orders_roof_visibility_attributes.roof_visibility_attribute_id = roof_visibility_attributes.id

      WHERE orders_roof_visibility_attributes.mark_for_delete IS NOT TRUE
            AND roof_visibility_attributes.mark_for_delete IS NOT TRUE

      GROUP BY orders_roof_visibility_attributes.order_id
  ),

  -- the roof estimate IS done WHEN an estimate WITH a level of >= 7 IS return to slayer.
  -- the roof estimate will go through the payment state machine AND THEN get release to the customer
    roof_estimate_done AS (SELECT
                             estimatable_id
                             , min(created_at) AS roof_estimate_returned_to_slayer_datetime
                           FROM alooma_slayer.hover_models_roof_estimates
                           WHERE level >= 7
                           GROUP BY estimatable_id

  )

--   get 1 row per job excluding clones AND examples
SELECT
    jobs.id                                                                             AS job_id
  , jobs.name                                                                           AS job_name
  , jobs.client_identifier                                                              AS job_client_identifier
  , models.manowar_identifier                                                           AS order_id
  , models.id                                                                           AS model_id
  , models.state                                                                        AS model_state
  , models.complexity_attributes_total_roof_facets_above_4_sqft                         AS model_complexity_attributes_total_roof_facets_above_4_sqft
  , models.complexity_attributes_roof_square_footage                                    AS model_complexity_attributes_roof_square_footage
  , models.complexity_attributes_total_roof_facets                                      AS model_complexity_attributes_total_roof_facets
  , models.reprocessed                                                                  AS model_reprocessed_indicator
  , models.complexity_score                                                             AS model_complexity_score
  , models.complexity_attributes_is_mfr                                                 AS model_is_mfr
  , model_transitions.first_upload_complete                                             AS job_first_upload_complete
  , model_transitions.first_finished_processing_upload                                  AS job_first_finished_processing_upload_datetime
  , model_transitions.first_finished_submitting                                         AS job_first_finished_submitting_datetime
  , model_transitions.first_finished_working                                            AS job_first_finished_working_datetime
  , model_transitions.first_finished_retrieving                                         AS job_first_finished_retrieving_datetime
  , model_transitions.first_finished_processing                                         AS job_first_finished_processing_datetime
  , model_transitions.first_finished_paying                                             AS job_first_finished_paying_datetime
  , model_transitions.from_waiting_approval                                             AS model_from_waiting_approval
  , model_transitions.to_waiting_approval                                               AS model_to_waiting_approval
  , mobile_applications.os                                                              AS mobile_application_os
  , mobile_applications.identifier                                                      AS mobile_application_identifier
  , roof_estimate_done.roof_estimate_returned_to_slayer_datetime
  , jobs.created_at                                                                     AS job_created_at
  , convert_timezone('utc', 'us/pacific', jobs.created_at)                              AS job_created_at_pt
  , jobs.updated_at                                                                     AS job_updated_at
  , convert_timezone('utc', 'us/pacific', jobs.updated_at)                              AS job_updated_at_pt
  , COALESCE(jobs.completed_at,
             CASE
             WHEN models.state = 'waiting_approval'
                  OR models.state = 'complete'
               THEN payments.first_paid_at
             END,
             model_transitions.max_completed_at)                                        AS job_completed_at
  , convert_timezone('utc', 'us/pacific', COALESCE(jobs.completed_at,
                                                   CASE
                                                   WHEN models.state = 'waiting_approval'
                                                        OR models.state = 'complete'
                                                     THEN payments.first_paid_at
                                                   END,
                                                   model_transitions.max_completed_at)) AS job_completed_at_pt
  , COALESCE(jobs.first_completed_at,
             CASE
             WHEN models.state = 'waiting_approval'
                  OR models.state = 'complete'
               THEN payments.first_paid_at
             END,
             model_transitions.min_completed_at)                                        AS job_first_completed_at
  , convert_timezone('utc', 'us/pacific', COALESCE(jobs.first_completed_at,
                                                   CASE
                                                   WHEN models.state = 'waiting_approval'
                                                        OR models.state = 'complete'
                                                     THEN payments.first_paid_at
                                                   END,
                                                   model_transitions.min_completed_at)) AS job_first_completed_at_pt
  , jobs.first_completed_at                                                             AS jobs_table_first_completed_at
  , jobs.approved                                                                       AS job_approved
  , jobs.approved_at                                                                    AS job_approved_at
  , convert_timezone('utc', 'us/pacific',
                     jobs.approved_at)                                                  AS job_approved_at_pt
  , jobs.customer_name                                                                  AS job_customer_name
  , jobs.customer_email                                                                 AS job_customer_email
  , jobs.customer_phone                                                                 AS job_customer_phone
  , jobs.customer_contact                                                               AS job_customer_contact
  , NVL(jobs.location_line_1, '') || ' ' || NVL(jobs.location_line_2, '') || ' ' || NVL(jobs.location_city, '')
    || ' ' || NVL(jobs.location_region, '') || ' ' || NVL(jobs.location_postal_code, '') || ' ' ||
    NVL(jobs.location_country, '')                                                      AS job_address
  , jobs.location_line_1                                                                AS job_location_line_1
  , jobs.location_line_2                                                                AS job_location_line_2
  , jobs.location_city                                                                  AS job_location_city
  , jobs.location_region                                                                AS job_location_region
  , jobs.location_country                                                               AS job_location_country
  , jobs.location_postal_code                                                           AS job_location_postal_code
  , COALESCE(nullif(location_lat, ''), NULL) :: double precision                        AS job_latitude
  , COALESCE(nullif(location_lon, ''), NULL) :: double precision                        AS job_longitude
  , jobs.e_deliverable_name                                                             AS job_deliverable
  , jobs.e_roof_estimate_access_level_name                                              AS job_roof_estimate_access_level_name
  , jobs.original_job_id                                                                AS job_original_id
  , jobs.example                                                                        AS job_example
  , jobs.external_identifier                                                            AS job_external_identifier
  , jobs.captured_user_id                                                               AS job_captured_user_id
  , job_assignments.org_id                                                              AS job_assignments_org_id
  , job_assignments.user_id                                                             AS job_assignments_user_id
  , job_assignments.job_id                                                              AS job_assignments_job_id
  , orgs.id                                                                             AS org_id
  , orgs.name                                                                           AS org_name
  , orgs.created_at                                                                     AS org_created_datetime
  , orgs.created_at :: date                                                             AS orgs_created_date
  , orgs.ancestral_name                                                                 AS org_ancestral_name
  , orgs.plan_billing_cycle                                                             AS org_plan_billing_cycle
  , wallets.stripe_customer_identifier                                                  AS wallet_stripe_customer_identifier
  , COALESCE(wallets.card_last4, 'n')                                                   AS org_credit_card_on_file
  , wallets.billing_address_line_1                                                      AS wallet_billing_address_line_1
  , wallets.billing_address_line_2                                                      AS wallet_billing_address_line_2
  , wallets.billing_address_city                                                        AS wallet_billing_address_city
  , wallets.billing_address_region                                                      AS wallet_billing_address_region
  , wallets.billing_address_postal_code                                                 AS wallet_billing_address_postal_code
  , wallets.billing_address_country                                                     AS wallet_billing_address_country
  , plans.id                                                                            AS plan_id
  , plans.name                                                                          AS plan_name
  , plans.saas                                                                          AS plan_saas_indicator
  , partners.id                                                                         AS partner_id
  , partners.name                                                                       AS partner_name
  , partners.partner_or_industry                                                        AS partner_or_industry
  , affiliates.affiliate_ids
  , affiliates.affiliate_names
  , affiliates.symbility_affiliate
  , affiliates.num_affiliates
  , payments.payment_complexities
  , payments.payment_deliverables
  , COALESCE(payments.base_price, 0)                                                                 AS payments_base_price
  , COALESCE(payments.discount, 0)                                                                   AS payments_discount
  , COALESCE(payments.balance_debit, 0)                                                              AS payments_post_tax_balance_debit
  , COALESCE(payments.base_price_subsidy, 0)                                                         AS payments_base_price_subsidy
  , COALESCE(payments.discount_subsidy, 0)                                                           AS payments_discount_subsidy
  , COALESCE(payments.tax, 0)                                                                        AS payments_tax
  , COALESCE(payments.subtotal, 0)                                                                   AS payments_post_tax_subtotal
  , COALESCE(payments.total, 0)                                                                      AS payments_credit_card
  , COALESCE(payments.pre_tax_balance_debit, 0)                                                      AS payments_pre_tax_balance_debit
  , COALESCE(payments.pre_tax_subtotal, 0)                                                           AS payments_pre_tax_subtotal
  , COALESCE(payments.invoiced_amount, 0)                                                            AS payments_invoice
  , COALESCE(payments.gross_revenue, 0)                                                              AS gross_job_revenue
  , COALESCE(payments.gross_customer_revenue, 0)                                                     AS gross_customer_revenue
  , COALESCE(payments.gross_job_refunded_revenue, 0)                                                 AS gross_job_refunded_revenue
  , payments.first_paid_at                                                              AS payments_first_paid_at
  , convert_timezone('utc', 'us/pacific', payments.first_paid_at)                       AS payments_first_paid_at_pt
  , payments.first_refunded_at                                                          AS payments_first_refunded_at
  , convert_timezone('utc', 'us/pacific', payments.first_refunded_at)                   AS payments_first_refunded_at_pt
  , users.id                                                                            AS user_id
  , users.email                                                                         AS user_email
  , split_part(users.email, '@', 2)                                                     AS user_email_domain
  , users.created_at                                                                    AS user_created_at
  , convert_timezone('utc', 'us/pacific', users.created_at)                             AS user_created_at_pt
  , users.first_name || ' ' || users.last_name                                          AS user_name
  , users.first_name                                                                    AS user_first_name
  , users.last_name                                                                     AS user_last_name
  , users.office_phone                                                                  AS user_office_phone
  , users.mobile_phone                                                                  AS user_mobile_phone
  , users.provider                                                                      AS user_provider
  , users.preferred_identifier                                                          AS user_preferred_identifier
  , account.id                                                                          AS salesforce_account_id
  , account.tier__c                                                                     AS salesforce_account_tier
  , account.total_annual_estimate__c                                                    AS salesforce_account_total_annual_potential_jobs
  , account.total_potential_users__c                                                    AS salesforce_account_total_potential_users
  , account.sales__c                                                                    AS salesforce_account_sales_methodology
  , account.contractor_membership_program__c                                            AS salesforce_account_contractor_membership_program
  , account.source__c                                                                   AS salesforce_account_source
  , account.source_detail__c                                                            AS salesforce_account_source_detail
  , account.insurance__c                                                                AS salesforce_account_insurance
  , account.roofing__c                                                                  AS salesforce_account_roofing
  , account.siding__c                                                                   AS salesforce_account_siding
  , account.crm__c                                                                      AS salesforce_account_crm
  , account.region__c                                                                   AS salesforce_account_region
  , account.industry                                                                    AS salesforce_account_industry
  , account.total_revenue__c                                                            AS salesforce_account_total_estimate_org_revenue
  , account.industry_ent__c                                                             AS salesforce_account_industry_vertical
  , account.estimating_platform__c                                                      AS salesforce_account_estimating_platform
  , account.measurement_provider__c                                                     AS salesforce_account_measurement_provider
  , account.symbility_integration__c                                                    AS salesforce_account_symbility_integration
  , account.settle_onsite__c                                                            AS salesforce_account_settle_onsite
  , account.size_of_contractor_network__c                                               AS salesforce_account_size_of_contractor_network
  , account.size_of_adjuster_network__c                                                 AS salesforce_account_size_of_adjuster_network
  , account.desk_adjusting_team__c                                                      AS salesforce_account_desk_adjusting_team
  , account.number_of_field_adjusters__c                                                AS salesforce_account_number_of_field_adjusters
  , COALESCE(account.org_grouping__c, orgs.name + '_' + orgs.id :: varchar)             AS org_grouping
  , account.high_independent_adjuster_use__c                                            AS salesforce_account_high_independent_adjuster_use
  , salesforce_owner_user.name                                                          AS salesforce_account_owner_name
  , salesforce_owner_user.id                                                            AS salesforce_account_owner_id
  , owner_userrole.name                                                                 AS salesforce_account_owner_role_name
  , salesforce_outside_user.name                                                        AS salesforce_account_outside_account_exec_name
  , salesforce_outside_user.id                                                          AS salesforce_account_outside_account_exec_id
  , orders.e_failure_reason_name                                                        AS order_failure_reason
  , orders.e_priority_name                                                              AS order_priority
  , orders.e_image_score_name                                                           AS order_image_score
  , orders.e_number_of_stories_name                                                     AS order_number_of_stories
  , orders.e_difficulty_name                                                            AS order_difficulty
  , orders.map_attributes_source
  , orders.needs_roof_estimate                                                          AS order_needs_roof_estimate
  , orders.one_call_close                                                               AS order_one_call_close
  , orders.sub_hour_possible                                                            AS order_sub_hour_possible
  , orders.created_at                                                                   AS order_created_datetime
  , orthotag_list_orders.orthotag_list
  , hover_models_roof_estimates.results_sq_ftg_estimate                                 AS roof_estimate
  , hover_models_roof_estimates.estimated_pitch                                         AS pitch_estimate
  , hover_models_roof_estimates.level_list                                              AS level_list
  , fail_times.failed_datetime                                                          AS order_last_failed_at
  , earliest_user.org_earliest_user_created_at                                          AS org_earliest_user_created_at
  , convert_timezone('utc', 'us/pacific', earliest_user.org_earliest_user_created_at)   AS org_earliest_user_created_at_pt
  , payments.job_payment_first_paid_at
  , payments.roof_estimate_payment_first_paid_at
  , payments.job_payment_first_refunded_at
  , payments.roof_estimate_payment_first_refunded_at
  , payments.first_deliverable_paid_for_id
  , payments.first_deliverable_paid_for_name

  -- plan, discount, AND saas payment information at the time the job was created
  , orgs_plans_partners_history_created.start_datetime                                  AS orgs_plans_history_start_datetime_job_created
  , orgs_plans_partners_history_created.adjusted_end_datetime                           AS orgs_plans_history_end_datetime_job_created
  , orgs_plans_partners_history_created.org_id                                          AS orgs_plans_history_org_id_job_created
  , orgs_plans_partners_history_created.org_name                                        AS orgs_plans_history_org_name_job_created
  , orgs_plans_partners_history_created.plan_id                                         AS orgs_plans_history_plan_id_job_created
  , orgs_plans_partners_history_created.plan_name                                       AS orgs_plans_history_plan_name_job_created
  , orgs_plans_partners_history_created.plan_partner_id                                 AS orgs_plans_history_partner_id_job_created
  , orgs_plans_partners_history_created.partner_name                                    AS orgs_plans_history_partner_name_job_created
  , orgs_plans_partners_history_created.plan_monthly_price                              AS orgs_plans_history_monthly_price_job_created
  , orgs_plans_partners_history_created.plan_yearly_price                               AS orgs_plans_history_yearly_price_job_created
  , orgs_plans_partners_history_created.plan_has_monthly_and_yearly_prices              AS orgs_plans_history_has_monthly_and_yearly_prices_job_created
  , orgs_plans_partners_history_created.plan_saas                                       AS orgs_plans_history_plan_saas_job_created

  , trial_discounts_created.discount_id                                                 AS trial_discounts_discount_id_job_created
  , trial_discounts_created.trial_discount_start_datetime                               AS trial_discounts_start_datetime_job_created
  , trial_discounts_created.trial_discount_end_datetime                                 AS trial_discounts_end_datetime_job_created
  , trial_discounts_created.discount_name                                               AS trial_discounts_discount_name_job_created
  , trial_discounts_created.row_source                                                  AS trial_discounts_row_source_job_created

  , saas_payments_created.saas_payment_id                                               AS saas_payment_id_job_created
  , saas_payments_created.saas_payment_good_data                                        AS saas_payment_good_data_job_created
  , saas_payments_created.saas_payment_term_length                                      AS saas_payment_term_length_job_created
  , saas_payments_created.saas_next_payment_term_length                                 AS saas_next_payment_term_length_job_created
  , saas_payments_created.saas_term_start_datetime                                      AS saas_term_start_datetime_job_created
  , saas_payments_created.saas_term_expected_end_datetime                               AS saas_term_expected_end_datetime_job_created
  , saas_payments_created.saas_term_end_datetime                                        AS saas_term_end_datetime_job_created
  , saas_payments_created.saas_next_payment_created_datetime                            AS saas_next_payment_created_datetime_job_created
  , saas_payments_created.saas_absolute_seconds_between_payments_created_at             AS saas_absolute_seconds_between_payments_created_job_created
  , saas_payments_created.saas_payment_stripe_charge_identifier                         AS saas_payment_stripe_charge_identifier_job_created
  , saas_payments_created.saas_payment_gross_revenue                                    AS saas_payment_gross_revenue_job_created
  , saas_payments_created.saas_payment_paid_datetime                                    AS saas_payment_paid_datetime_job_created

  -- plan, discount, AND saas payment information at the time the job was first complete
  , orgs_plans_partners_history_first_completed.start_datetime                          AS orgs_plans_history_start_datetime_job_first_completed
  , orgs_plans_partners_history_first_completed.adjusted_end_datetime                   AS orgs_plans_history_end_datetime_job_first_completed
  , orgs_plans_partners_history_first_completed.org_id                                  AS orgs_plans_history_org_id_job_first_completed
  , orgs_plans_partners_history_first_completed.org_name                                AS orgs_plans_history_org_name_job_first_completed
  , orgs_plans_partners_history_first_completed.plan_id                                 AS orgs_plans_history_plan_id_job_first_completed
  , orgs_plans_partners_history_first_completed.plan_name                               AS orgs_plans_history_plan_name_job_first_completed
  , orgs_plans_partners_history_first_completed.plan_partner_id                         AS orgs_plans_history_partner_id_job_first_completed
  , orgs_plans_partners_history_first_completed.partner_name                            AS orgs_plans_history_partner_name_job_first_completed
  , orgs_plans_partners_history_first_completed.plan_monthly_price                      AS orgs_plans_history_monthly_price_job_first_completed
  , orgs_plans_partners_history_first_completed.plan_yearly_price                       AS orgs_plans_history_yearly_price_job_first_completed
  , orgs_plans_partners_history_first_completed.plan_has_monthly_and_yearly_prices      AS orgs_plans_history_has_monthly_and_yearly_prices_job_first_completed
  , orgs_plans_partners_history_first_completed.plan_saas                               AS orgs_plans_history_plan_saas_job_first_completed

  , trial_discounts_first_completed.discount_id                                         AS trial_discounts_discount_id_job_first_completed
  , trial_discounts_first_completed.trial_discount_start_datetime                       AS trial_discounts_start_datetime_job_first_completed
  , trial_discounts_first_completed.trial_discount_end_datetime                         AS trial_discounts_end_datetime_job_first_completed
  , trial_discounts_first_completed.discount_name                                       AS trial_discounts_discount_name_job_first_completed
  , trial_discounts_first_completed.row_source                                          AS trial_discounts_row_source_job_first_completed

  , saas_payments_first_completed.saas_payment_id                                       AS saas_payment_id_job_first_completed
  , saas_payments_first_completed.saas_payment_good_data                                AS saas_payment_good_data_job_first_completed
  , saas_payments_first_completed.saas_payment_term_length                              AS saas_payment_term_length_job_first_completed
  , saas_payments_first_completed.saas_next_payment_term_length                         AS saas_next_payment_term_length_job_first_completed
  , saas_payments_first_completed.saas_term_start_datetime                              AS saas_term_start_datetime_job_first_completed
  , saas_payments_first_completed.saas_term_expected_end_datetime                       AS saas_term_expected_end_datetime_job_first_completed
  , saas_payments_first_completed.saas_term_end_datetime                                AS saas_term_end_datetime_job_first_completed
  , saas_payments_first_completed.saas_next_payment_created_datetime                    AS saas_next_payment_created_datetime_job_first_completed
  , saas_payments_first_completed.saas_absolute_seconds_between_payments_created_at     AS saas_absolute_seconds_between_payments_created_job_first_completed
  , saas_payments_first_completed.saas_payment_stripe_charge_identifier                 AS saas_payment_stripe_charge_identifier_job_first_completed
  , saas_payments_first_completed.saas_payment_gross_revenue                            AS saas_payment_gross_revenue_job_first_completed
  , saas_payments_first_completed.saas_payment_paid_datetime                            AS saas_payment_paid_datetime_job_first_completed

  -- plan, discount, AND saas payment information at the time the job was most recently complete
  , orgs_plans_partners_history_completed.start_datetime                                AS orgs_plans_history_start_datetime_job_completed
  , orgs_plans_partners_history_completed.adjusted_end_datetime                         AS orgs_plans_history_end_datetime_job_completed
  , orgs_plans_partners_history_completed.org_id                                        AS orgs_plans_history_org_id_job_completed
  , orgs_plans_partners_history_completed.org_name                                      AS orgs_plans_history_org_name_job_completed
  , orgs_plans_partners_history_completed.plan_id                                       AS orgs_plans_history_plan_id_job_completed
  , orgs_plans_partners_history_completed.plan_name                                     AS orgs_plans_history_plan_name_job_completed
  , orgs_plans_partners_history_completed.plan_partner_id                               AS orgs_plans_history_partner_id_job_completed
  , orgs_plans_partners_history_completed.partner_name                                  AS orgs_plans_history_partner_name_job_completed
  , orgs_plans_partners_history_completed.plan_monthly_price                            AS orgs_plans_history_monthly_price_job_completed
  , orgs_plans_partners_history_completed.plan_yearly_price                             AS orgs_plans_history_yearly_price_job_completed
  , orgs_plans_partners_history_completed.plan_has_monthly_and_yearly_prices            AS orgs_plans_history_has_monthly_and_yearly_prices_job_completed
  , orgs_plans_partners_history_completed.plan_saas                                     AS orgs_plans_history_plan_saas_job_completed

  , trial_discounts_completed.discount_id                                               AS trial_discounts_discount_id_job_completed
  , trial_discounts_completed.trial_discount_start_datetime                             AS trial_discounts_start_datetime_job_completed
  , trial_discounts_completed.trial_discount_end_datetime                               AS trial_discounts_end_datetime_job_completed
  , trial_discounts_completed.discount_name                                             AS trial_discounts_discount_name_job_completed
  , trial_discounts_completed.row_source                                                AS trial_discounts_row_source_job_completed

  , saas_payments_completed.saas_payment_id                                             AS saas_payment_id_job_completed
  , saas_payments_completed.saas_payment_good_data                                      AS saas_payment_good_data_job_completed
  , saas_payments_completed.saas_payment_term_length                                    AS saas_payment_term_length_job_completed
  , saas_payments_completed.saas_next_payment_term_length                               AS saas_next_payment_term_length_job_completed
  , saas_payments_completed.saas_term_start_datetime                                    AS saas_term_start_datetime_job_completed
  , saas_payments_completed.saas_term_expected_end_datetime                             AS saas_term_expected_end_datetime_job_completed
  , saas_payments_completed.saas_term_end_datetime                                      AS saas_term_end_datetime_job_completed
  , saas_payments_completed.saas_next_payment_created_datetime                          AS saas_next_payment_created_datetime_job_completed
  , saas_payments_completed.saas_absolute_seconds_between_payments_created_at           AS saas_absolute_seconds_between_payments_created_job_completed
  , saas_payments_completed.saas_payment_stripe_charge_identifier                       AS saas_payment_stripe_charge_identifier_job_completed
  , saas_payments_completed.saas_payment_gross_revenue                                  AS saas_payment_gross_revenue_job_completed
  , saas_payments_completed.saas_payment_paid_datetime                                  AS saas_payment_paid_datetime_job_completed
  , org_settings.invoiced                                                               AS org_setting_invoiced
  , org_settings.machete_features                                                       AS org_setting_machete_features
  , org_settings.priority                                                               AS org_setting_priority
  , org_settings.vip                                                                    AS org_setting_vip

  , search_indices.id                                                                   AS search_indices_id
  , search_indices.filters_types                                                        AS search_indices_filters_types
  , (search_indices.filters_types IN ('["connect"]', '["prospect","connect"]'))         AS hover_connect_indicator
  , (search_indices.filters_types IN ('["prospect"]', '["prospect","connect"]'))        AS hover_prospect_indicator
  , CASE
    WHEN hover_connect_indicator
         AND hover_prospect_indicator
      THEN 'connect AND prospect'
    WHEN hover_connect_indicator
      THEN 'connect'
    WHEN hover_prospect_indicator
      THEN 'prospect'
    WHEN search_indices.filters_types = '["standard"]'
      THEN 'standard'
    END                                                                                 AS job_type
  , search_indices.filters_deliverable_ids                                              AS search_indices_deliverable_ids
  , (search_indices.filters_deliverable_ids like '%%4%%')                               AS hover_now_in_search_indices
  , CASE
    WHEN hover_now_in_search_indices IS TRUE
      THEN 'now'
    WHEN hover_prospect_indicator IS TRUE AND extract(second FROM (model_transitions.first_finished_processing - jobs.approved_at)) < 0
      THEN 'prospect - model built before approval'
    WHEN hover_prospect_indicator AND jobs.approved_at >= model_transitions.first_upload_complete
      THEN 'prospect'
    ELSE 'upload complete to finished processing'
    END                                                                                 AS customer_turn_around_time_calculation_case
  , CASE
    --   hover now - first upload complete to roof estimate sent back to slayer
    WHEN hover_now_in_search_indices IS TRUE
      THEN extract(second FROM (roof_estimate_done.roof_estimate_returned_to_slayer_datetime - model_transitions.first_upload_complete))
    --   prospect - approved at to finished processing.  if we built the model before it's approved this IS 0.
    WHEN hover_prospect_indicator IS TRUE AND extract(second FROM (model_transitions.first_finished_processing - jobs.approved_at)) < 0
      THEN 0
    --  prospect - approved before we built the model
    WHEN hover_prospect_indicator IS TRUE AND jobs.approved_at >= model_transitions.first_upload_complete
      THEN extract(second FROM (model_transitions.first_finished_processing - jobs.approved_at))
    --   ALL other jobs - finished upload complete to finished processing
    ELSE extract(second FROM (model_transitions.first_finished_processing - model_transitions.first_finished_processing_upload))
    END                                                                                 AS customer_turn_around_time_seconds
  , CASE
    WHEN hover_now_in_search_indices IS TRUE
      THEN extract(second FROM (roof_estimate_done.roof_estimate_returned_to_slayer_datetime - model_transitions.first_upload_complete)) / 60.0
    WHEN hover_prospect_indicator IS TRUE AND extract(second FROM (model_transitions.first_finished_processing - jobs.approved_at)) < 0
      THEN 0.0
    WHEN hover_prospect_indicator IS TRUE AND jobs.approved_at >= model_transitions.first_upload_complete
      THEN extract(second FROM (model_transitions.first_finished_processing - jobs.approved_at)) / 60.0
    ELSE extract(second FROM (model_transitions.first_finished_processing - model_transitions.first_finished_processing_upload)) / 60.0
    END                                                                                 AS customer_turn_around_time_minutes
  , CASE
    WHEN hover_now_in_search_indices IS TRUE
      THEN extract(second FROM (roof_estimate_done.roof_estimate_returned_to_slayer_datetime - model_transitions.first_upload_complete)) / 3600.0
    WHEN hover_prospect_indicator IS TRUE AND extract(second FROM (model_transitions.first_finished_processing - jobs.approved_at)) < 0
      THEN 0.0
    WHEN hover_prospect_indicator IS TRUE AND jobs.approved_at >= model_transitions.first_upload_complete
      THEN extract(second FROM (model_transitions.first_finished_processing - jobs.approved_at)) / 3600.0
    ELSE extract(second FROM (model_transitions.first_finished_processing - model_transitions.first_finished_processing_upload)) / 3600.0
    END                                                                                 AS customer_turn_around_time_hours


FROM alooma_slayer.jobs jobs
  --    WHEN models IS merged WITH jobs this subquery can be turned into a normal JOIN
  JOIN (
         SELECT
           id
           , job_id
           , manowar_identifier
           , state
           , complexity_attributes_total_roof_facets_above_4_sqft
           , complexity_attributes_roof_square_footage
           , complexity_attributes_total_roof_facets
           , complexity_attributes_is_mfr
           , reprocessed
           --   https://github.com/hoverinc/hyperion/commit/9ae400b212fb6beedf1e031170dc36325c104cba#diff-925c941166913c7b03d2f62cab604358l418
           , CASE
             WHEN created_at :: date <= '2017-04-12' AND complexity_attributes_roof_square_footage IS NOT NULL
               THEN
                 CASE WHEN complexity_attributes_roof_square_footage > 4000
                   THEN 'large'
                 WHEN complexity_attributes_roof_square_footage > 2000
                   THEN 'medium'
                 --          200 was the small threshold. i don'y understand the old code thresholds
                 ELSE 'small' END
             WHEN complexity_attributes_total_roof_facets_above_4_sqft IS NOT NULL
               THEN
                 CASE WHEN complexity_attributes_total_roof_facets_above_4_sqft > 22
                   THEN 'custom'
                 WHEN complexity_attributes_total_roof_facets_above_4_sqft > 16
                   THEN 'large'
                 WHEN complexity_attributes_total_roof_facets_above_4_sqft > 4
                   THEN 'medium'
                 ELSE 'small' END
             ELSE NULL
             END AS complexity_score
           , created_at
           , mark_for_delete

         FROM alooma_slayer.models
         WHERE models.mark_for_delete IS NOT TRUE
               AND models.id IN (SELECT min(id)
                                 FROM alooma_slayer.models
                                 GROUP BY job_id)
       ) models ON models.job_id = jobs.id
  JOIN alooma_slayer.org_job_accesses org_job_accesses
    ON jobs.id = org_job_accesses.job_id AND org_job_accesses.kind = 0
  LEFT JOIN alooma_slayer.search_indices
    ON search_indices.searchable_id = jobs.id
       AND search_indices.searchable_type = 'job'
  JOIN alooma_slayer.orgs orgs ON orgs.id = org_job_accesses.org_id
  JOIN alooma_slayer.plans plans ON plans.id = orgs.plan_id
  JOIN alooma_slayer.partners partners ON partners.id = plans.partner_id
  LEFT JOIN (
              SELECT
                affiliates_partners.partner_id
                , COUNT(affiliates.id)           AS num_affiliates
                , listagg(affiliates.id, ', ')   AS affiliate_ids
                , listagg(affiliates.name, ', ') AS affiliate_names
                , COUNT(CASE WHEN affiliates.name = 'symbility'
                THEN affiliates.id END) > 0      AS symbility_affiliate
              FROM alooma_slayer.affiliates_partners
                LEFT JOIN alooma_slayer.affiliates ON affiliates_partners.affiliate_id = affiliates.id
              WHERE affiliates.deleted_at IS NULL
                    AND affiliates_partners.deleted_at IS NULL
              GROUP BY
                affiliates_partners.partner_id
            ) affiliates
    ON partners.id = affiliates.partner_id
  JOIN alooma_slayer.wallets wallets ON wallets.org_id = orgs.id

  JOIN alooma_slayer.job_assignments job_assignments
    ON jobs.id = job_assignments.job_id
       AND job_assignments.kind = 0
       AND job_assignments.deleted != 'TRUE'
       AND job_assignments.hard_deleted_at IS NULL

  JOIN alooma_slayer.users users ON users.id = job_assignments.user_id
  LEFT JOIN alooma_slayer.mobile_applications mobile_applications ON mobile_applications.id = jobs.mobile_application_id
  LEFT JOIN alooma_salesforce.account account ON account.hyperion_id__c = orgs.id
  LEFT JOIN alooma_salesforce."user" salesforce_owner_user ON salesforce_owner_user.id = account.ownerid
  LEFT JOIN alooma_salesforce."user" salesforce_outside_user ON salesforce_outside_user.id = account.outside_account_exec__c
  LEFT JOIN alooma_salesforce.userrole owner_userrole ON owner_userrole.id = salesforce_owner_user.userroleid
  LEFT JOIN alooma_manowar.orders orders ON orders.id = models.manowar_identifier
  JOIN alooma_slayer.org_settings ON orgs.id = org_settings.org_id
  LEFT JOIN (SELECT
               org_id
               , min(users.created_at) AS org_earliest_user_created_at

             FROM (
                    SELECT
                      accesses.user_id
                      , accesses.org_id

                    FROM alooma_slayer.accesses accesses
                    WHERE accesses.mark_for_delete IS NOT TRUE
                    UNION ALL
                    SELECT
                      job_assignments.user_id
                      , org_job_accesses.org_id

                    FROM alooma_slayer.org_job_accesses
                      JOIN alooma_slayer.job_assignments job_assignments
                        ON org_job_accesses.job_id = job_assignments.job_id AND job_assignments.kind = 0
                    WHERE org_job_accesses.kind = 0
                          AND org_job_accesses.mark_for_delete IS NOT TRUE
                          AND job_assignments.mark_for_delete IS NOT TRUE
                          AND job_assignments.mark_for_delete IS NOT TRUE
                          AND job_assignments.deleted != 'TRUE'
                          AND job_assignments.hard_deleted_at IS NULL
                  ) all_orgs_users
               LEFT JOIN alooma_slayer.users users
                 ON users.id = all_orgs_users.user_id
             WHERE users.is_test_data IS NOT TRUE
                   AND users.mark_for_delete IS NOT TRUE

             GROUP BY org_id) earliest_user

    ON (earliest_user.org_id = orgs.id)

  LEFT JOIN public.payments_job_and_roof_estimates payments ON payments.job_id = jobs.id

  LEFT JOIN (
              SELECT
                order_id
                , MAX(created_at) AS failed_datetime
              FROM alooma_manowar.complete_failed_order_state_transitions
              WHERE "to" = 'failed'
                    AND complete_failed_order_state_transitions.mark_for_delete IS NOT TRUE
              GROUP BY order_id
            ) fail_times ON models.manowar_identifier = fail_times.order_id

  LEFT JOIN (
              SELECT
                model_id
                , min(CASE WHEN event = 'finished_uploading'
                THEN created_at
                      ELSE NULL END) AS first_upload_complete
                , min(CASE WHEN event = 'finished_processing_upload'
                THEN created_at
                      ELSE NULL END) AS first_finished_processing_upload
                , min(CASE WHEN event = 'finished_submitting'
                THEN created_at
                      ELSE NULL END) AS first_finished_submitting
                , min(CASE WHEN event = 'finished_working'
                THEN created_at
                      ELSE NULL END) AS first_finished_working
                , min(CASE WHEN event = 'finished_retrieving'
                THEN created_at
                      ELSE NULL END) AS first_finished_retrieving
                , min(CASE WHEN event = 'finished_processing'
                THEN created_at
                      ELSE NULL END) AS first_finished_processing
                , min(CASE WHEN event = 'finished_paying'
                THEN created_at
                      ELSE NULL END) AS first_finished_paying
                , min(CASE WHEN "FROM" = 'waiting_approval'
                THEN created_at
                      ELSE NULL END) AS from_waiting_approval
                , min(CASE WHEN "to" = 'waiting_approval'
                THEN created_at
                      ELSE NULL END) AS to_waiting_approval
                , min(CASE WHEN "to" = 'complete'
                THEN created_at
                      ELSE NULL END) AS min_completed_at
                , MAX(CASE WHEN "to" = 'complete'
                THEN created_at
                      ELSE NULL END) AS max_completed_at
              FROM alooma_slayer.model_state_transitions
              WHERE model_state_transitions.mark_for_delete IS NOT TRUE
              GROUP BY model_id
            ) model_transitions ON model_transitions.model_id = models.id


  --    JOIN for dimensional information at the time the job was created
  LEFT JOIN public.orgs_plans_partners_history orgs_plans_partners_history_created
    ON orgs_plans_partners_history_created.org_id = org_job_accesses.org_id

  --   JOIN for dimensional information at the time the job was first completed
  LEFT JOIN public.orgs_plans_partners_history orgs_plans_partners_history_first_completed
    ON orgs_plans_partners_history_first_completed.org_id = org_job_accesses.org_id
       AND ((COALESCE(jobs.first_completed_at, payments.first_paid_at) BETWEEN orgs_plans_partners_history_first_completed.start_datetime AND orgs_plans_partners_history_first_completed.adjusted_end_datetime)
            OR (COALESCE(jobs.first_completed_at, payments.first_paid_at) < orgs_plans_partners_history_first_completed.start_datetime AND orgs_plans_partners_history_first_completed.org_plan_rank = 1))


  --   JOIN for dimensional information at the time the job was most recently completed
  LEFT JOIN public.orgs_plans_partners_history orgs_plans_partners_history_completed
    ON orgs_plans_partners_history_completed.org_id = org_job_accesses.org_id
       AND ((COALESCE(jobs.completed_at, payments.first_paid_at) BETWEEN orgs_plans_partners_history_completed.start_datetime AND orgs_plans_partners_history_completed.adjusted_end_datetime)
            OR (COALESCE(jobs.completed_at, payments.first_paid_at) < orgs_plans_partners_history_completed.start_datetime
                AND orgs_plans_partners_history_completed.org_plan_rank = 1))


  LEFT JOIN public.trial_discounts trial_discounts_created
    ON (trial_discounts_created.org_id = org_job_accesses.org_id
        AND jobs.created_at BETWEEN trial_discounts_created.trial_discount_start_datetime AND trial_discounts_created.trial_discount_end_datetime)

  LEFT JOIN public.trial_discounts trial_discounts_first_completed
    ON (trial_discounts_first_completed.org_id = org_job_accesses.org_id
        AND (COALESCE(jobs.first_completed_at, payments.first_paid_at) BETWEEN trial_discounts_first_completed.trial_discount_start_datetime AND trial_discounts_first_completed.trial_discount_end_datetime))

  LEFT JOIN public.trial_discounts trial_discounts_completed
    ON (trial_discounts_completed.org_id = org_job_accesses.org_id
        AND (COALESCE(jobs.completed_at, payments.first_paid_at) BETWEEN trial_discounts_completed.trial_discount_start_datetime AND trial_discounts_completed.trial_discount_end_datetime))

  LEFT JOIN public.payments_saas saas_payments_created
    ON (saas_payments_created.org_id = org_job_accesses.org_id
        AND jobs.created_at BETWEEN saas_payments_created.saas_term_start_datetime AND saas_payments_created.saas_term_end_datetime)

  LEFT JOIN public.payments_saas saas_payments_first_completed
    ON (saas_payments_first_completed.org_id = org_job_accesses.org_id
        AND (COALESCE(jobs.first_completed_at, payments.first_paid_at) BETWEEN saas_payments_first_completed.saas_term_start_datetime AND saas_payments_first_completed.saas_term_end_datetime))

  LEFT JOIN public.payments_saas saas_payments_completed
    ON (saas_payments_completed.org_id = org_job_accesses.org_id
        AND (COALESCE(jobs.completed_at, payments.first_paid_at) BETWEEN saas_payments_completed.saas_term_start_datetime AND saas_payments_completed.saas_term_end_datetime))

  LEFT JOIN hover_models_roof_estimates ON orders.id = hover_models_roof_estimates.order_id
                                           AND hover_models_roof_estimates.id IN (SELECT MAX(id) AS id
                                                                                  FROM alooma_manowar.hover_models_roof_estimates
                                                                                  GROUP BY estimatable_id)
  LEFT JOIN orthotag_list_orders ON orders.id = orthotag_list_orders.order_id

  LEFT JOIN roof_estimate_done ON roof_estimate_done.estimatable_id = jobs.id


WHERE jobs.mark_for_delete IS NOT TRUE
      AND org_job_accesses.mark_for_delete IS NOT TRUE
      AND org_job_accesses.deleted IS NOT TRUE
      AND orgs.mark_for_delete IS NOT TRUE
      AND plans.mark_for_delete IS NOT TRUE
      AND partners.mark_for_delete IS NOT TRUE
      AND wallets.mark_for_delete IS NOT TRUE
      AND job_assignments.mark_for_delete IS NOT TRUE
      AND users.mark_for_delete IS NOT TRUE
      AND users.is_test_data IS NOT TRUE
      AND orgs.is_test_data IS NOT TRUE
      AND jobs.example IS NOT TRUE
      AND search_indices.mark_for_delete IS NOT TRUE
      --   ensure we only get 1 model per job. jobs can have many models though only a handful actually do. takes the first model WHEN there IS more than 1.
      --   get the row BETWEEN the start date OR the 1st row IN the table otherwise
      AND (
        (jobs.created_at BETWEEN orgs_plans_partners_history_created.start_datetime AND orgs_plans_partners_history_created.adjusted_end_datetime)
        OR (jobs.created_at < orgs_plans_partners_history_created.start_datetime
            AND orgs_plans_partners_history_created.org_plan_rank = 1))
      AND org_settings.mark_for_delete IS NOT TRUE
      AND jobs.test_state = 0
