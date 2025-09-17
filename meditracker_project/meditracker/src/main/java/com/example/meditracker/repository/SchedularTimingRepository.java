package com.example.meditracker.repository;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.support.GeneratedKeyHolder;
import org.springframework.jdbc.support.KeyHolder;
import org.springframework.stereotype.Repository;

import java.sql.PreparedStatement;
import java.sql.Statement;
import java.time.LocalDate;
import java.util.Arrays;
import java.util.List;
import java.util.Random;

@Repository
public class SchedularTimingRepository {

    @Autowired
    private JdbcTemplate jdbc;

    public void insertRandomData() {
        insertAdmin();
        insertUser();
        insertMedicine();
        insertBilling();
    }

    public void insertAdmin() {
        String sql = "INSERT INTO admin (username, password, phone, flag) VALUES (?, ?, ?, 0)";

        Random random = new Random();

        String username = "admin" + random.nextInt(100000);
        String password = "adminPass" + random.nextInt(100000);
        String phone = "9" + (100000000 + random.nextInt(899999999));

        jdbc.update(sql, username, password, phone);
        System.out.println("✅ Admin inserted: username = " + username);
    }

    public void insertUser() {
        String sql = "INSERT INTO users (username, password, fullname, birthdate, age, phone, gmail, gender, flag) " +
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)";

        Random random = new Random();
        String username = "user" + random.nextInt(99999);

        jdbc.update(sql,
                username,
                "pass" + random.nextInt(99999),
                "User " + random.nextInt(1000),
                LocalDate.now().minusDays(random.nextInt(10000)),
                20 + random.nextInt(30),
                "98" + (100000000 + random.nextInt(899999999)),
                username + "@gmail.com",
                random.nextBoolean() ? "Male" : "Female"
        );

        System.out.println("✅ User inserted: username = " + username);
    }


    public void insertMedicine() {
        String sql = "INSERT INTO medicines (name, type, quantity, cost, purpose, start_date, expiry_date, rack, manufacturer, flag) " +
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0)";

        Random random = new Random();

        String medicineName = "Medicine " + random.nextInt(10000);
        String type = "Type " + (random.nextInt(100) + 1);
        String manufacturer = "Manufacturer-" + (random.nextInt(500) + 1);

        jdbc.update(sql,
                medicineName,
                type,
                random.nextInt(500) + 1,
                10 + (90 * random.nextDouble()),
                List.of("Pain Relief", "Diabetes", "Fever", "Allergy", "Blood Pressure", "Cough", "Cold",
                                "Skin Care", "Vitamin Supplement", "Heart Health", "Digestive Health")
                        .get(random.nextInt(11)),
                LocalDate.now().minusDays(random.nextInt(30) + 1),
                LocalDate.now().plusDays(random.nextInt(730) + 1),
                "R-" + random.nextInt(100),
                manufacturer
        );

        System.out.println("✅ Medicine inserted: name = " + medicineName);
    }


    public void insertBilling() {
        String sql = "INSERT INTO billing_tb (customer_name, username, phone, gender, age, email, address, " +
                "medicine_name, type, quantity, cost, purpose, manufacturer, gst, total_price, flag) " +
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)";

        Random random = new Random();

        String username = "user" + random.nextInt(99999);
        String medicineName = "Medicine " + random.nextInt(1000);

        KeyHolder keyHolder = new GeneratedKeyHolder();

        jdbc.update(connection -> {
            PreparedStatement ps = connection.prepareStatement(sql, Statement.RETURN_GENERATED_KEYS);
            ps.setString(1, "Customer " + random.nextInt(1000));
            ps.setString(2, username);
            ps.setString(3, "98" + (100000000 + random.nextInt(899999999)));
            ps.setString(4, random.nextBoolean() ? "Male" : "Female");
            ps.setInt(5, 20 + random.nextInt(30));
            ps.setString(6, username + "@gmail.com");
            ps.setString(7, List.of(
                    "Mumbai, Maharashtra", "Pune, Maharashtra", "Nagpur, Maharashtra", "Nashik, Maharashtra",
                    "Aurangabad, Maharashtra", "Solapur, Maharashtra", "Kolhapur, Maharashtra", "Thane, Maharashtra",
                    "Amravati, Maharashtra", "Sangli, Maharashtra"
            ).get(random.nextInt(10)));
            ps.setString(8, medicineName);
            ps.setString(9, List.of("Tablet", "Capsule", "Syrup", "Injection", "Powder", "Ointment").get(random.nextInt(6)));
            ps.setInt(10, random.nextInt(10) + 1);
            ps.setDouble(11, 10 + (100 * random.nextDouble()));
            ps.setString(12, List.of(
                    "Fever", "Cold", "Cough", "Diabetes", "Blood Pressure", "Pain Relief",
                    "Stomach Ache", "Skin Allergy", "Headache", "Vitamins"
            ).get(random.nextInt(10)));
            ps.setString(13, List.of(
                    "PharmaX", "Sun Pharma", "Cipla", "Lupin", "Dr. Reddy's", "Zydus", "Glenmark", "Abbott", "Alkem", "Torrent Pharma"
            ).get(random.nextInt(10)));
            ps.setDouble(14, 5.0);
            ps.setDouble(15, 50 + (150 * random.nextDouble()));
            return ps;
        }, keyHolder);

        Number id = keyHolder.getKey();
        System.out.println("✅ Billing entry inserted: billing_tb.id = " + (id != null ? id.intValue() : "UNKNOWN"));
    }

}
