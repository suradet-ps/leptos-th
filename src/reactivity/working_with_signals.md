# การทำงานกับสัญญาณ

จนถึงตอนนี้ เราได้ใช้ตัวอย่างง่ายๆ ของการใช้ [`signal`](https://docs.rs/leptos/latest/leptos/reactive/signal/fn.signal.html) ซึ่งคืนค่าเก็ตเตอร์ [`ReadSignal`](https://docs.rs/leptos/latest/leptos/reactive/signal/struct.ReadSignal.html) และเซ็ตเตอร์ [`WriteSignal`](https://docs.rs/leptos/latest/leptos/reactive/signal/struct.WriteSignal.html)

## การอ่านค่าและการตั้งค่า

มีการดำเนินการพื้นฐานกับสัญญาณอยู่ไม่กี่อย่าง:

### การอ่านค่า

1. [`.read()`](https://docs.rs/leptos/latest/leptos/reactive/signal/struct.ReadSignal.html#impl-Read-for-T) คืนค่าการ์ดการอ่าน (read guard) ซึ่งดีรีเฟอเรนซ์ไปยังค่าของสัญญาณ และติดตามการเปลี่ยนแปลงของค่าสัญญาณในอนาคตแบบรีแอกทีฟ โปรดทราบว่าคุณไม่สามารถอัปเดตค่าของสัญญาณได้จนกว่าการ์ดนี้จะถูกดรอป ไม่เช่นนั้นจะเกิดข้อผิดพลาดขณะรันไทม์
1. [`.with()`](https://docs.rs/leptos/latest/leptos/reactive/signal/struct.ReadSignal.html#impl-With-for-T) รับฟังก์ชัน ซึ่งจะได้รับค่าปัจจุบันของสัญญาณแบบอ้างอิง (`&T`) และติดตามสัญญาณนั้น
1. [`.get()`](https://docs.rs/leptos/latest/leptos/reactive/signal/struct.ReadSignal.html#impl-Get-for-T) โคลนค่าปัจจุบันของสัญญาณ และติดตามการเปลี่ยนแปลงของค่าดังกล่าวต่อไป

`.get()` เป็นเมธอดที่ใช้บ่อยที่สุดในการเข้าถึงสัญญาณ `.read()` มีประโยชน์สำหรับเมธอดที่รับรีเฟอเรนซ์แบบไม่เปลี่ยนค่า โดยไม่ต้องโคลนค่า (`my_vec_signal.read().len()`) ส่วน `.with()` มีประโยชน์เมื่อคุณต้องทำอะไรมากกว่านั้นกับรีเฟอเรนซ์นั้น แต่ยังต้องการมั่นใจว่าคุณไม่ได้ถือล็อกไว้นานเกินความจำเป็น

### การตั้งค่า

1. [`.write()`](https://docs.rs/leptos/latest/leptos/reactive/signal/struct.WriteSignal.html#impl-Write-for-WriteSignal%3CT,+S%3E) คืนค่าการ์ดการเขียน (write guard) ซึ่งเป็นรีเฟอเรนซ์แบบเปลี่ยนแปลงได้ไปยังค่าของสัญญาณ และแจ้งเตือนผู้ติดตามทั้งหมดว่าพวกเขาต้องอัปเดต โปรดทราบว่าคุณไม่สามารถอ่านค่าของสัญญาณได้จนกว่าการ์ดนี้จะถูกดรอป ไม่เช่นนั้นจะเกิดข้อผิดพลาดขณะรันไทม์
1. [`.update()`](https://docs.rs/leptos/latest/leptos/reactive/signal/struct.WriteSignal.html#impl-Update-for-T) รับฟังก์ชัน ซึ่งจะได้รับรีเฟอเรนซ์แบบเปลี่ยนแปลงได้ไปยังค่าปัจจุบันของสัญญาณ (`&mut T`) และแจ้งเตือนผู้ติดตาม (`.update()` ไม่คืนค่าที่โคลเชอร์คืนมา แต่คุณใช้ [`.try_update()`](https://docs.rs/leptos/latest/leptos/trait.SignalUpdate.html#tymethod.try_update) ได้หากจำเป็น เช่น หากคุณกำลังลบสมาชิกออกจาก `Vec<_>` และต้องการสมาชิกที่ถูกลบนั้น)
1. [`.set()`](https://docs.rs/leptos/latest/leptos/reactive/signal/struct.WriteSignal.html#impl-Set-for-T) แทนที่ค่าปัจจุบันของสัญญาณและแจ้งเตือนผู้ติดตาม

`.set()` เป็นวิธีที่ใช้บ่อยที่สุดในการตั้งค่าใหม่ ส่วน `.write()` มีประโยชน์มากสำหรับการอัปเดตค่าในที่เดิม เช่นเดียวกับกรณีของ `.read()` และ `.with()` นั้น `.update()` มีประโยชน์เมื่อคุณต้องการหลีกเลี่ยงความเป็นไปได้ที่จะถือล็อกการเขียนไว้นานกว่าที่ตั้งใจ

```admonish note
แทรตเหล่านี้สร้างขึ้นจากการประกอบกันของแทรตและมาพร้อมอิมพลีเมนเทชันแบบแบล็งเก็ต ตัวอย่างเช่น `Read` ถูกอิมพลีเมนต์ให้กับชนิดใดๆ ที่อิมพลีเมนต์ `Track` และ `ReadUntracked` ส่วน `With` ถูกอิมพลีเมนต์ให้กับชนิดใดๆ ที่อิมพลีเมนต์ `Read` และ `Get` ถูกอิมพลีเมนต์ให้กับชนิดใดๆ ที่อิมพลีเมนต์ `With` และ `Clone` เป็นต้น

ความสัมพันธ์ในลักษณะเดียวกันนี้มีอยู่สำหรับ `Write`, `Update` และ `Set` ด้วย

เรื่องนี้ควรค่าแก่การจดจำเมื่ออ่านเอกสาร: หากคุณเห็นว่ามีเพียง `ReadUntracked` และ `Track` เท่านั้นที่เป็นแทรตที่ถูกอิมพลีเมนต์ คุณก็ยังสามารถใช้ `.with()`, `.get()` (ถ้า `T: Clone`) และอื่นๆ ได้
```

## การทำงานกับสัญญาณ

คุณอาจสังเกตได้ว่า `.get()` และ `.set()` สามารถอิมพลีเมนต์โดยอาศัย `.read()` และ `.write()` หรือ `.with()` และ `.update()` ได้ กล่าวอีกนัยหนึ่ง `count.get()` ให้ผลเหมือนกับ `count.with(|n| n.clone())` หรือ `count.read().clone()` และ `count.set(1)` ถูกอิมพลีเมนต์โดยทำ `count.update(|n| *n = 1)` หรือ `*count.write() = 1`

แต่แน่นอนว่า `.get()` และ `.set()` มีไวยากรณ์ที่สวยงามกว่า

อย่างไรก็ตาม ยังมีกรณีการใช้งานที่ดีมากสำหรับเมธอดอื่นๆ

ตัวอย่างเช่น ลองพิจารณาสัญญาณที่เก็บ `Vec<String>`

```rust
let (names, set_names) = signal(Vec::new());
if names.get().is_empty() {
	set_names(vec!["Alice".to_string()]);
}
```

ในแง่ของลอจิกนั้น เรื่องนี้ง่ายพอสมควร แต่มันซ่อนความไม่มีประสิทธิภาพที่สำคัญไว้ จำไว้ว่า `names.get().is_empty()` โคลนค่า นั่นหมายความว่าเราโคลน `Vec<String>` ทั้งก้อน รัน `is_empty()` แล้วทิ้งสำเนานั้นทันที

เช่นเดียวกัน `set_names` แทนที่ค่าด้วย `Vec<_>` ก้อนใหม่ทั้งหมด ซึ่งก็ไม่เป็นไร แต่เราน่าจะกลายพันธุ์ `Vec<_>` ต้นฉบับในที่เดิมไปเลยจะดีกว่า

```rust
let (names, set_names) = signal(Vec::new());
if names.read().is_empty() {
	set_names.write().push("Alice".to_string());
}
```

ตอนนี้ฟังก์ชันของเรารับ `names` แบบอ้างอิงเพื่อรัน `is_empty()` หลีกเลี่ยงการโคลนนั้น แล้วกลายพันธุ์ `Vec<_>` ในที่เดิม

## ความปลอดภัยของเธรดและค่าประจำเธรด

คุณอาจสังเกตได้ ไม่ว่าจะจากการอ่านเอกสารหรือจากการทดลองกับแอปพลิเคชันของคุณเอง ว่าค่าที่ถูกเก็บอยู่ในสัญญาณต้องเป็น `Send + Sync` ที่เป็นเช่นนี้เพราะระบบรีแอกทีฟรองรับการทำงานแบบหลายเธรดจริงๆ สัญญาณสามารถถูกส่งข้ามเธรดได้ และกราฟรีแอกทิวิตีทั้งกราฟก็สามารถทำงานข้ามหลายเธรดได้ (เรื่องนี้มีประโยชน์เป็นพิเศษเมื่อทำ[การเรนเดอร์ฝั่งเซิร์ฟเวอร์](../ssr/) ด้วยเฟรมเวิร์กฝั่งเซิร์ฟเวอร์อย่าง Axum ซึ่งใช้ตัวรันแบบหลายเธรดของ Tokio) ในกรณีส่วนใหญ่ เรื่องนี้ไม่มีผลต่อสิ่งที่คุณทำ เพราะชนิดข้อมูล Rust ทั่วไปเป็น `Send + Sync` โดยค่าเริ่มต้นอยู่แล้ว

อย่างไรก็ตาม สภาพแวดล้อมของเบราว์เซอร์นั้นเป็นแบบเธรดเดียว เว้นแต่คุณจะใช้ Web Worker และชนิดข้อมูล JavaScript ที่ `wasm-bindgen` และ `web-sys` มอบให้ล้วนเป็น `!Send` อย่างชัดเจน ซึ่งหมายความว่าพวกมันไม่สามารถถูกเก็บในสัญญาณธรรมดาได้

ด้วยเหตุนี้ เราจึงมีทางเลือกแบบ “โลคอล” สำหรับพรีมิทีฟของสัญญาณแต่ละตัว ซึ่งใช้เก็บข้อมูล `!Send` ได้ คุณควรเลือกใช้สิ่งเหล่านี้เฉพาะเมื่อคุณมีชนิดข้อมูลเบราว์เซอร์แบบ `!Send` ที่ต้องเก็บไว้ในสัญญาณเท่านั้น

| มาตรฐาน | โลคอล |
| -------- | ----- |
| [`signal`](https://docs.rs/leptos/latest/leptos/reactive/signal/fn.signal.html) | [`signal_local`](https://docs.rs/leptos/latest/leptos/prelude/fn.signal_local.html) |
| [`RwSignal::new`](https://docs.rs/leptos/latest/leptos/prelude/struct.RwSignal.html#method.new) | [`RwSignal::new_local`](https://docs.rs/leptos/latest/leptos/prelude/struct.RwSignal.html#method.new_local) |
| [`Resource`](https://docs.rs/leptos/latest/leptos/prelude/struct.Resource.html) | [`LocalResource`](https://docs.rs/leptos/latest/leptos/prelude/struct.LocalResource.html) |
| [`Action::new`](https://docs.rs/leptos/latest/leptos/prelude/struct.Action.html#method.new) | [`Action::new_local`](https://docs.rs/leptos/latest/leptos/prelude/struct.Action.html#method.new_local), [`Action::new_unsync`](https://docs.rs/leptos/latest/leptos/prelude/struct.Action.html#method.new_unsync) |

## ไวยากรณ์ nightly

เมื่อใช้ฟีเชอร์ `nightly` และไวยากรณ์ `nightly` การเรียก `ReadSignal` เป็นฟังก์ชันถือเป็นน้ำตาลไวยากรณ์ของ `.get()` ส่วนการเรียก `WriteSignal` เป็นฟังก์ชันถือเป็นน้ำตาลไวยากรณ์ของ `.set()` ดังนั้น

```rust
let (count, set_count) = signal(0);
set_count(1);
logging::log!(count());
```

จึงเทียบเท่ากับ

```rust
let (count, set_count) = signal(0);
set_count.set(1);
logging::log!(count.get());
```

นี่ไม่ใช่แค่น้ำตาลไวยากรณ์เท่านั้น แต่ยังทำให้ API สอดคล้องกันมากขึ้นด้วยการทำให้สัญญาณเป็นสิ่งเดียวกับฟังก์ชันในเชิงความหมาย: ดู[คั่นรายการ](./interlude_functions.md)

## การทำให้สัญญาณขึ้นต่อกัน

บ่อยครั้งที่ผู้คนถามถึงสถานการณ์ที่สัญญาณหนึ่งจำเป็นต้องเปลี่ยนไปตามค่าของสัญญาณอื่น มีสามวิธีที่ดีในการทำเช่นนี้ และอีกวิธีหนึ่งที่ยังห่างจากอุดมคติแต่ก็พอใช้ได้ในสถานการณ์ที่ควบคุมได้

### ทางเลือกที่ดี

**1) B เป็นฟังก์ชันของ A** สร้างสัญญาณสำหรับ A และสร้างสัญญาณอนุพัทธ์หรือเมโมสำหรับ B

```rust
// A
let (count, set_count) = signal(1);
// B is a function of A
let derived_signal_double_count = move || count.get() * 2;
// B is a function of A
let memoized_double_count = Memo::new(move |_| count.get() * 2);
```

> สำหรับคำแนะนำว่าควรใช้สัญญาณอนุพัทธ์หรือเมโม ดูเอกสารของ [`Memo`](https://docs.rs/leptos/latest/leptos/reactive/computed/struct.Memo.html)

**2) C เป็นฟังก์ชันของ A และสิ่งอื่นอีกอย่างคือ B** สร้างสัญญาณสำหรับ A และ B และสร้างสัญญาณอนุพัทธ์หรือเมโมสำหรับ C

```rust
// A
let (first_name, set_first_name) = signal("Bridget".to_string());
// B
let (last_name, set_last_name) = signal("Jones".to_string());
// C is a function of A and B
let full_name = move || format!("{} {}", &*first_name.read(), &*last_name.read());
```

**3) A และ B เป็นสัญญาณอิสระต่อกัน แต่บางครั้งก็ถูกอัปเดตพร้อมกัน** เมื่อคุณเรียกอัปเดต A ให้เรียกอัปเดต B แยกต่างหากด้วย

```rust
// A
let (age, set_age) = signal(32);
// B
let (favorite_number, set_favorite_number) = signal(42);
// use this to handle a click on a `Clear` button
let clear_handler = move |_| {
  // update both A and B
  set_age.set(0);
  set_favorite_number.set(0);
};
```

### ถ้าคุณจำเป็นจริงๆ...

**4) สร้างเอฟเฟกต์เพื่อเขียนค่าไปยัง B ทุกครั้งที่ A เปลี่ยน** วิธีนี้ไม่ได้รับการสนับสนุนอย่างเป็นทางการด้วยเหตุผลหลายประการ:
a) มันจะไม่มีประสิทธิภาพเสมอ เพราะหมายความว่าทุกครั้งที่ A อัปเดต คุณต้องเดินครบสองรอบผ่านกระบวนการรีแอกทีฟ (คุณตั้งค่า A ซึ่งทำให้เอฟเฟกต์รัน รวมถึงเอฟเฟกต์อื่นๆ ที่ขึ้นกับ A จากนั้นคุณตั้งค่า B ซึ่งทำให้เอฟเฟกต์ใดๆ ที่ขึ้นกับ B รัน)
b) มันเพิ่มโอกาสที่คุณจะสร้างสิ่งอย่างลูปอนันต์หรือเอฟเฟกต์ที่รันซ้ำเกินจำเป็นโดยไม่ตั้งใจ นี่คือโค้ดสปาเกตตีแบบรีแอกทีฟที่ปิงปองไปมา ซึ่งพบได้ทั่วไปในช่วงต้นทศวรรษ 2010 และเป็นสิ่งที่เราพยายามหลีกเลี่ยงด้วยสิ่งต่างๆ เช่น การแยกการอ่านและการเขียนออกจากกัน และการไม่สนับสนุนให้เขียนค่าลงในสัญญาณจากเอฟเฟกต์

ในสถานการณ์ส่วนใหญ่ ทางที่ดีที่สุดคือเขียนใหม่ให้มีโฟลว์ข้อมูลจากบนลงล่างที่ชัดเจนโดยอิงจากสัญญาณอนุพัทธ์หรือเมโม แต่นี่ก็ไม่ใช่จุดจบของโลก

> ผมตั้งใจไม่ยกตัวอย่างไว้ที่นี่ อ่านเอกสารของ [`Effect`](https://docs.rs/leptos/latest/leptos/reactive/effect/struct.Effect.html) เพื่อดูว่าสิ่งนี้จะทำงานได้อย่างไร
