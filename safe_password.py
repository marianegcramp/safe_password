#!/usr/bin/env python3


from PySide import QtCore, QtGui
import string
import random


class CharsetBuilder:
    def __init__(self):
        self.included_chars = ''
        self.excluded_chars = ''

    def include_chars(self, chars):
        self.included_chars += chars
        return self

    def exclude_chars(self, chars):
        self.excluded_chars += chars
        return self

    def build(self):
        self.included_chars = ''.join(set(self.included_chars))
        self.excluded_chars = ''.join(set(self.excluded_chars))

        charset = ''
        for char in self.included_chars:
            if not char in self.excluded_chars:
                charset += char

        return charset


class PasswordGenerator:
    def generate_password(self, length, unique_chars, charset):
        if unique_chars:
            return ''.join(random.sample(charset, length))
        else:
            return ''.join(random.choice(charset) for i in range(length))


class PasswordRulesValidator:
    def __init__(self):
        self.error = None

    def validate_rules(self, length, unique, charset):
        if len(charset) == 0:
            self.error = 'A charset is empty.'
            return False

        if unique and length > len(charset):
            self.error = 'The charset is too short.'
            return False

        return True


class PresentTwoOtherCharsRule:
    def is_satisfied(self, password):
        return any(password.count(char) < len(password) for char in password)


class PresentCharsubsetsRule:
    def __init__(self, charsubsets, present_charsubsets_min):
        self.charsubsets = charsubsets
        self.present_charsubsets_min = present_charsubsets_min

    def is_satisfied(self, password):
        present_charsubsets = [False] * len(self.charsubsets)

        for char in password:
            for i in range(0, len(self.charsubsets)):
                if char in self.charsubsets[i]:
                    present_charsubsets[i] = True

        if present_charsubsets.count(True) >= self.present_charsubsets_min:
            return True
        else:
            return False


class MinimumLengthRule:
    def __init__(self, min_length):
        self.min_length = min_length

    def is_satisfied(self, password):
        return len(password) >= self.min_length


class PasswordStrengthCounter:
    def __init__(self):
        charsubsets = [string.ascii_lowercase, string.ascii_uppercase, string.digits, string.punctuation]

        self.rules = [
            (MinimumLengthRule(1), 20.0),
            (MinimumLengthRule(8), 20.0),
            (PresentTwoOtherCharsRule(), 20.0),
            (PresentCharsubsetsRule(charsubsets, 2), 20.0),
            (PresentCharsubsetsRule(charsubsets, 3), 20.0)
        ]

    def count_strength(self, password):
        total_weight = 0.0

        for rule, weight in self.rules:
            if rule.is_satisfied(password):
                total_weight += weight
            else:
                break

        return total_weight / 100.0


class PasswordStrengthWidget(QtGui.QWidget):
    def __init__(self, parent=None, strength=0.0):
        super().__init__(parent=parent)
        self.strength = strength

        self.setMinimumWidth(100)
        self.setMinimumHeight(16)

    def set_strength(self, strength):
        self.strength = strength
        self.repaint()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)

        w = self.width()
        h = self.height()

        painter.fillRect(0, 0, w, h, QtCore.Qt.white)
        painter.fillRect(0, 0, w*self.strength, h, self.get_color_for_strength())

    def get_color_for_strength(self):
        if self.strength <= 0.4:
            color = QtCore.Qt.red
        elif self.strength <= 0.6:
            color = QtCore.Qt.yellow
        elif self.strength <= 0.8:
            color = QtCore.Qt.blue
        else:
            color = QtCore.Qt.green

        return color


class PasswordGeneratorWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.password_generator = PasswordGenerator()
        self.password_rules_validator = PasswordRulesValidator()
        self.password_strength_counter = PasswordStrengthCounter()

        self.setWindowTitle('Safe password')

        main_layout = QtGui.QVBoxLayout()

        password_settings_group = QtGui.QGroupBox('Password settings')
        password_settings_layout = QtGui.QVBoxLayout()
        password_length_layout = QtGui.QHBoxLayout()
        password_length_label = QtGui.QLabel('Password length: ', self)
        password_length_layout.addWidget(password_length_label)
        self.password_length_spinbox = QtGui.QSpinBox(self)
        self.password_length_spinbox.setRange(1, 128)
        password_length_layout.addWidget(self.password_length_spinbox)
        password_settings_layout.addLayout(password_length_layout)
        self.password_unique_check = QtGui.QCheckBox('Don\'t repeat chars')
        password_settings_layout.addWidget(self.password_unique_check)
        password_settings_group.setLayout(password_settings_layout)
        main_layout.addWidget(password_settings_group)

        charset_settings_group = QtGui.QGroupBox('Charset settings')
        charset_settings_layout = QtGui.QVBoxLayout()
        self.lowercase_check = QtGui.QCheckBox('Include lowercase letters (abcd...)', self)
        charset_settings_layout.addWidget(self.lowercase_check)
        self.uppercase_check = QtGui.QCheckBox('Include uppercase letters (ABCD...)', self)
        charset_settings_layout.addWidget(self.uppercase_check)
        self.digits_check = QtGui.QCheckBox('Include digits (0123...)', self)
        charset_settings_layout.addWidget(self.digits_check)
        self.punctuation_check = QtGui.QCheckBox('Include punctuation chars (~!@#...)', self)
        charset_settings_layout.addWidget(self.punctuation_check)
        include_chars_label = QtGui.QLabel('Include custom chars:', self)
        charset_settings_layout.addWidget(include_chars_label)
        self.include_chars_edit = QtGui.QLineEdit(self)
        charset_settings_layout.addWidget(self.include_chars_edit)
        exclude_chars_label = QtGui.QLabel('Exclude custom chars:', self)
        charset_settings_layout.addWidget(exclude_chars_label)
        self.exclude_chars_edit = QtGui.QLineEdit(self)
        charset_settings_layout.addWidget(self.exclude_chars_edit)
        charset_settings_group.setLayout(charset_settings_layout)
        main_layout.addWidget(charset_settings_group)

        result_password_group = QtGui.QGroupBox('Your password')
        result_password_layout = QtGui.QVBoxLayout()
        self.result_password_edit = QtGui.QLineEdit()
        self.result_password_edit.setEchoMode(QtGui.QLineEdit.Password)
        result_password_layout.addWidget(self.result_password_edit)
        self.password_strength_widget = PasswordStrengthWidget(self)
        result_password_layout.addWidget(self.password_strength_widget)
        result_password_group.setLayout(result_password_layout)
        main_layout.addWidget(result_password_group)

        buttons_layout = QtGui.QHBoxLayout()
        buttons_layout.addStretch()
        generate_button = QtGui.QPushButton('&Generate', self)
        generate_button.clicked.connect(self.on_generate_password)
        buttons_layout.addWidget(generate_button)
        copy_to_clipboard_button = QtGui.QPushButton('&Copy', self)
        copy_to_clipboard_button.clicked.connect(self.on_copy_to_clipboard)
        buttons_layout.addWidget(copy_to_clipboard_button)
        exit_button = QtGui.QPushButton('E&xit', self)
        exit_button.clicked.connect(self.close)
        buttons_layout.addWidget(exit_button)
        main_layout.addLayout(buttons_layout)

        main_layout.setSizeConstraint(QtGui.QLayout.SetFixedSize)
        self.setLayout(main_layout)

    @QtCore.Slot()
    def on_generate_password(self):
        length = self.password_length_spinbox.value()
        unique = self.password_unique_check.isChecked()
        charset = self.build_charset()
        if self.password_rules_validator.validate_rules(length, unique, charset):
            password = self.password_generator.generate_password(length, unique, charset)
            self.result_password_edit.setText(password)

            strength = self.password_strength_counter.count_strength(password)
            self.password_strength_widget.set_strength(strength)
        else:
            error = self.password_rules_validator.error
            QtGui.QMessageBox.critical(self, 'I\'m sorry', error)

    @QtCore.Slot()
    def on_copy_to_clipboard(self):
        clipboard = QtGui.QApplication.clipboard()
        clipboard.setText(self.result_password_edit.text())

    def build_charset(self):
        charset_builder = CharsetBuilder()

        if self.lowercase_check.isChecked():
            charset_builder.include_chars(string.ascii_lowercase)
        if self.uppercase_check.isChecked():
            charset_builder.include_chars(string.ascii_uppercase)
        if self.digits_check.isChecked():
            charset_builder.include_chars(string.digits)
        if self.punctuation_check.isChecked():
            charset_builder.include_chars(string.punctuation)

        include_chars = self.include_chars_edit.text()
        charset_builder.include_chars(include_chars)

        exclude_chars = self.exclude_chars_edit.text()
        charset_builder.exclude_chars(exclude_chars)

        return charset_builder.build()


if __name__ == '__main__':
    app = QtGui.QApplication([])
    win = PasswordGeneratorWidget()
    win.show()
    app.exec_()
